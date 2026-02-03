"""
Real-time Detection Endpoint - YOLO Version
WebSocket endpoint for real-time object detection with bounding boxes
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import base64
import cv2
import numpy as np
import logging
from PIL import Image
import io
import time
from typing import Dict, List, Optional, Set
import json

from app.core.config import settings
from app.core.database import get_db
from app.core.model_loader import get_model
from app.models.classification import ClassificationHistory
from app.utils.image_preprocessing import preprocess_image_for_detection
from sqlalchemy.orm import Session

router = APIRouter()
logger = logging.getLogger(__name__)

from app.utils.bin_mapping import map_class_to_bin


class DetectionTracker:
    """
    Tracks detections across frames for stability
    Uses IoU matching and temporal smoothing
    """
    
    def __init__(
        self,
        smoothing_alpha: float = 0.6,
        min_confidence: float = 0.35,
        min_frames: int = 3,
        min_duration_ms: float = 500,
        iou_threshold: float = 0.3
    ):
        """
        Args:
            smoothing_alpha: EMA smoothing factor (0-1), higher = more responsive
            min_confidence: Minimum confidence for new detections
            min_frames: Minimum consecutive frames before reporting
            min_duration_ms: Minimum duration in ms before reporting
            iou_threshold: IoU threshold for matching detections
        """
        self.smoothing_alpha = smoothing_alpha
        self.min_confidence = min_confidence
        self.min_frames = min_frames
        self.min_duration_ms = min_duration_ms
        self.iou_threshold = iou_threshold
        
        # Track active objects
        self.tracked_objects = {}  # {track_id: TrackedObject}
        self.next_track_id = 0
        self.logged_ids: Set[int] = set() # Track IDs that have already been logged to DB
        
    def calculate_iou(self, box1: List[int], box2: List[int]) -> float:
        """Calculate Intersection over Union between two boxes"""
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2
        
        # Calculate intersection
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        
        if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
            return 0.0
        
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        
        # Calculate union
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0.0
    
    def smooth_box(self, current_box: List[int], previous_box: List[int]) -> List[int]:
        """Apply exponential moving average to box coordinates"""
        alpha = self.smoothing_alpha
        return [
            int(alpha * curr + (1 - alpha) * prev)
            for curr, prev in zip(current_box, previous_box)
        ]
    
    def update(self, raw_detections: List[Dict]) -> List[Dict]:
        """
        Update tracker with new detections with advanced safeguards
        """
        current_time = time.time() * 1000
        
        # Match detections to existing tracks
        matched_tracks = set()
        unmatched_detections = []
        
        for detection in raw_detections:
            from app.utils.bin_mapping import VN_TO_EN_CLASS_NAMES
            class_en = VN_TO_EN_CLASS_NAMES.get(detection['class_name'], detection['class_name'].lower())
            
            # --- HEURISTIC: Class-aware sensitivity ---
            effective_min_conf = self.min_confidence
            if class_en in ["biological", "paper"]:
                effective_min_conf = min(effective_min_conf, 0.20)
            
            best_iou = 0
            best_track_id = None
            
            # Find best matching track
            for track_id, tracked_obj in self.tracked_objects.items():
                iou = self.calculate_iou(detection['box'], tracked_obj['box'])
                if iou > best_iou and iou >= self.iou_threshold:
                    best_iou = iou
                    best_track_id = track_id
            
            if best_track_id is not None:
                tracked_obj = self.tracked_objects[best_track_id]
                
                # --- HEURISTIC: Hysteresis (Keep-alive threshold) ---
                # Once an object is tracked, we can be more lenient to keep it (0.8x threshold)
                keep_alive_threshold = effective_min_conf * 0.8 * 100
                if detection['confidence'] < keep_alive_threshold:
                    continue

                # --- HEURISTIC: Size Stability Check ---
                curr_box = detection['box']
                prev_box = tracked_obj['box']
                curr_area = (curr_box[2] - curr_box[0]) * (curr_box[3] - curr_box[1])
                prev_area = (prev_box[2] - prev_box[0]) * (prev_box[3] - prev_box[1])
                
                if prev_area > 0:
                    area_growth = curr_area / prev_area
                    if area_growth > 2.5: 
                        if tracked_obj['class_name_en'] == "battery" and detection['confidence'] < 80:
                            unmatched_detections.append(detection)
                            continue

                # --- HEURISTIC: Confidence-Weighted Smoothing ---
                # Higher confidence detections should have more weight (higher alpha)
                trust_factor = min(1.0, detection['confidence'] / 100)
                dynamic_alpha = self.smoothing_alpha * (0.5 + 0.5 * trust_factor)
                
                # Manual smoothing with dynamic alpha
                tracked_obj['box'] = [
                    int(dynamic_alpha * curr + (1 - dynamic_alpha) * prev)
                    for curr, prev in zip(detection['box'], tracked_obj['box'])
                ]
                
                # --- HEURISTIC: Class Consistency (Anti-Flicker) ---
                # Track class history to prevent jumping between types
                tracked_obj['class_history'].append(detection['class_name'])
                if len(tracked_obj['class_history']) > 3: # Shorter history for better responsiveness
                    tracked_obj['class_history'].pop(0)
                
                # Only update the primary class if the new class is dominant in history
                most_common_class = max(set(tracked_obj['class_history']), key=tracked_obj['class_history'].count)
                if tracked_obj['class_history'].count(most_common_class) >= 2:
                    tracked_obj['class_name'] = most_common_class
                    tracked_obj['class_name_en'] = VN_TO_EN_CLASS_NAMES.get(most_common_class, most_common_class.lower())
                    tracked_obj['bin_type'] = map_class_to_bin(most_common_class).value

                tracked_obj['confidence'] = detection['confidence']
                tracked_obj['frame_count'] += 1
                tracked_obj['last_seen'] = current_time
                matched_tracks.add(best_track_id)
            else:
                # New detection - needs full threshold to start a track
                if detection['confidence'] >= effective_min_conf * 100:
                    unmatched_detections.append(detection)
        
        # Create new tracks
        for detection in unmatched_detections:
            track_id = self.next_track_id
            self.next_track_id += 1
            self.tracked_objects[track_id] = {
                'track_id': track_id,
                'box': detection['box'],
                'confidence': detection['confidence'],
                'class_name': detection['class_name'],
                'class_name_en': detection['class_name_en'],
                'class_history': [detection['class_name']],
                'bin_type': detection['bin_type'],
                'frame_count': 1,
                'first_seen': current_time,
                'last_seen': current_time
            }
        
        # Remove stale tracks
        stale_threshold = current_time - 500
        stale_tracks = [tid for tid, obj in self.tracked_objects.items() if obj['last_seen'] < stale_threshold]
        for tid in stale_tracks:
            # If a track becomes stale, it's no longer active, so remove it from logged_ids
            if tid in self.logged_ids:
                self.logged_ids.remove(tid)
            del self.tracked_objects[tid]
        
        # Return stable detections
        stable_detections = []
        for track_id, tracked_obj in self.tracked_objects.items():
            duration = current_time - tracked_obj['first_seen']
            
            effective_min_frames = self.min_frames
            effective_min_duration = self.min_duration_ms
            
            x1, y1, x2, y2 = tracked_obj['box']
            area_ratio = ((x2 - x1) * (y2 - y1)) / (640 * 480)
            
            if tracked_obj['class_name_en'] in ["biological", "paper"]:
                if area_ratio > 0.10: 
                    effective_min_frames = 2  
                    effective_min_duration = 300 
                else:
                    effective_min_frames = 4 
                    effective_min_duration = 700
                
            if (tracked_obj['frame_count'] >= effective_min_frames and 
                duration >= effective_min_duration):
                stable_detections.append({
                    'box': tracked_obj['box'],
                    'confidence': tracked_obj['confidence'],
                    'class_name': tracked_obj['class_name'],
                    'class_name_en': tracked_obj['class_name_en'],
                    'bin_type': tracked_obj['bin_type'],
                    'detection_id': track_id,
                    'frame_count': tracked_obj['frame_count'],
                    'duration_ms': round(duration, 0)
                })
        
        stable_detections.sort(key=lambda x: x['confidence'], reverse=True)
        return stable_detections


def process_frame_yolo(model, image: Image.Image) -> Dict:
    """
    Process frame with YOLO model
    
    Args:
        model: YOLO model
        image: PIL Image
        
    Returns:
        Detection results with boxes and classes
    """
    start_time = time.time()
    
    # Convert PIL to numpy array (RGB)
    image_np = np.array(image)
    
    # Run YOLO prediction (stream mode for realtime)
    # Note: We skip low-light preprocessing here to maintain high FPS
    # unless it's strictly required by user configuration
    try:
        # --- HEURISTIC: Use lower baseline confidence for prediction ---
        # This allows us to "catch" objects that YOLO is slightly unsure about
        # but manual filtering later (using CLASS_SPECIFIC_CONF) ensures precision.
        results = model.predict(
            source=image_np,
            conf=0.15,  # Lower baseline for target classes
            iou=settings.IOU_THRESHOLD,
            imgsz=settings.IMAGE_SIZE,
            verbose=False,
            stream=False
        )
    except Exception as e:
        logger.error(f"❌ YOLO prediction failed: {e}")
        return {
            "detections": [],
            "total_objects": 0,
            "processing_time_ms": 0,
            "image_size": {"width": image.width, "height": image.height},
            "error": str(e)
        }
    
    # Parse results
    detections = []
    result = results[0]
    
    if result.boxes is not None and len(result.boxes) > 0:
        boxes = result.boxes
        
        from app.utils.bin_mapping import VN_TO_EN_CLASS_NAMES
        
        for idx, box in enumerate(boxes):
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            
            if cls < 0 or cls >= len(result.names):
                continue
            
            class_name_vn = result.names[cls]
            class_name_en = VN_TO_EN_CLASS_NAMES.get(class_name_vn, class_name_vn.lower())
            
            # --- HEURISTIC: Class-specific Threshold Filtering ---
            # Get the effective threshold for this class
            class_threshold = settings.CLASS_SPECIFIC_CONF.get(class_name_en, settings.CONF_THRESHOLD)
            
            if conf < class_threshold:
                continue
                
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            
            # --- HEURISTIC: Size Filtering ---
            # Avoid tiny background noise misidentified as paper/textile
            width = x2 - x1
            height = y2 - y1
            area_ratio = (width * height) / (640 * 480)
            aspect_ratio = width / height if height > 0 else 1.0
            
            # 1. Minimum Size Filtering (Noisy background)
            if class_name_en in ["paper", "cardboard", "textile"]:
                if area_ratio < 0.02: # Ignore objects smaller than 2% of frame
                    continue
            elif area_ratio < 0.01: # General noise filter (1%)
                continue
            
            # 2. Maximum Size Filtering (Oversized Hallucinations)
            # Detections like "Battery" should not cover half the screen
            constraints = settings.CLASS_SIZE_CONSTRAINTS.get(class_name_en)
            if constraints:
                max_area = constraints.get("max_area", 1.0)
                # If box is too large for this class
                if area_ratio > max_area:
                    # HEURISTIC: If box is oversized, it MUST have extremely high confidence (e.g., 0.85)
                    # to be accepted, otherwise it's likely catching background textures.
                    if conf < 0.85:
                        continue
                
                # 3. Aspect Ratio Check (Localization consistency)
                min_aspect = constraints.get("min_aspect")
                max_aspect = constraints.get("max_aspect")
                if min_aspect and aspect_ratio < min_aspect:
                    if conf < 0.80: # Reject if also uncertain
                        continue
                if max_aspect and aspect_ratio > max_aspect:
                    if conf < 0.80:
                        continue

            bin_type_enum = map_class_to_bin(class_name_vn)
            bin_type = bin_type_enum.value
            
            detection = {
                "box": [int(x1), int(y1), int(x2), int(y2)],
                "confidence": round(conf * 100, 1),
                "class_name": class_name_vn,
                "class_name_en": class_name_en,
                "bin_type": bin_type,
                "detection_id": idx
            }
            
            detections.append(detection)
    
    processing_time = (time.time() - start_time) * 1000  # Convert to ms
    
    # Sort by confidence (highest first)
    detections.sort(key=lambda x: x["confidence"], reverse=True)
    
    return {
        "detections": detections,
        "total_objects": len(detections),
        "processing_time_ms": round(processing_time, 2),
        "image_size": {
            "width": image.width,
            "height": image.height
        }
    }


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected: {websocket.client}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected: {websocket.client}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_detection(self, result: Dict, db: Session, tracker: DetectionTracker):
        """Broadcast detection result to all connected clients and save to DB if stable"""
        if not self.active_connections:
            return

        # Save stable detections to database for statistics
        if result.get("success") and result.get("data", {}).get("stable"):
            detections = result["data"].get("detections", [])
            if detections:
                primary = detections[0]
                track_id = primary.get("detection_id")
                
                # Only log once per track
                if track_id is not None and track_id not in tracker.logged_ids:
                    try:
                        history = ClassificationHistory(
                            class_name=primary["class_name_en"],
                            class_name_vn=primary["class_name"],
                            confidence=primary["confidence"],
                            bin_type=primary["bin_type"],
                            processing_time=result["metadata"].get("processing_time_ms", 0),
                            user_id="anonymous" # Placeholder, implement actual user tracking if needed
                        )
                        db.add(history)
                        db.commit()
                        tracker.logged_ids.add(track_id)
                        logger.info(f" [Stats] Recorded stable real-time detection: {primary['class_name']} (Track {track_id})")
                    except Exception as e:
                        db.rollback()
                        logger.error(f" [Stats] Failed to record real-time detection: {e}")

        for connection in self.active_connections:
            try:
                await connection.send_json(result)
            except WebSocketDisconnect:
                self.disconnect(connection)
            except Exception as e:
                logger.error(f"Error broadcasting to client {connection.client}: {e}")

manager = ConnectionManager()

@router.websocket("/ws/realtime-detect")
async def websocket_realtime_detect(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time YOLO detection
    """
    logger.info("📡 WebSocket connection attempt...")
    try:
        await manager.connect(websocket)
        logger.info("✅ WebSocket ACCEPTED!")
    except Exception as e:
        logger.error(f"❌ Failed to accept WebSocket: {e}")
        return

    frame_count = 0
    total_processing_time = 0
    
    # Create detection tracker for this connection
    tracker = DetectionTracker(
        smoothing_alpha=0.6,      # Responsive but smooth
        min_confidence=0.35,       # Higher threshold for initial detection
        min_frames=3,              # Must appear in 3 consecutive frames
        min_duration_ms=500,       # Must persist for 0.5 seconds
        iou_threshold=0.3          # IoU threshold for matching
    )
    logger.info("🎯 Detection tracker initialized")

    try:
        # Load YOLO model
        model = get_model()
        logger.info("🚀 YOLO model ready for realtime")

        while True:
            # Receive frame from client
            raw_data = await websocket.receive_text()
            frame_count += 1

            if not raw_data:
                continue

            # Debug first few frames
            if frame_count <= 3 or frame_count % 100 == 0:
                logger.info(f"📥 Frame {frame_count}: len={len(raw_data)}, sample={raw_data[:50]}...")

            try:
                processed_data = raw_data
                
                # 1. Handle JSON (either {"frame": "..."} or just a quoted string "\"abc...\"")
                try:
                    parsed = json.loads(raw_data)
                    if isinstance(parsed, dict):
                        # Try common keys
                        for key in ["frame", "image", "data", "img"]:
                            if key in parsed:
                                processed_data = parsed[key]
                                break
                        else:
                            # Use first string value if only one exists
                            string_vals = [v for v in parsed.values() if isinstance(v, str)]
                            if len(string_vals) == 1:
                                processed_data = string_vals[0]
                    elif isinstance(parsed, str):
                        processed_data = parsed
                except json.JSONDecodeError:
                    # Not JSON, keep as raw string
                    pass

                # 2. Remove Data URL prefix if present (e.g., "data:image/jpeg;base64,")
                if isinstance(processed_data, str) and ',' in processed_data:
                    processed_data = processed_data.split(',')[1]

                # 3. Decode Base64
                try:
                    img_bytes = base64.b64decode(processed_data)
                except Exception as b64_err:
                    logger.error(f"❌ Base64 decode failed for frame {frame_count}: {b64_err}")
                    raise ValueError(f"Invalid base64 data: {b64_err}")

                if not img_bytes:
                    raise ValueError("Received empty image bytes")

                # 4. Open Image
                try:
                    image = Image.open(io.BytesIO(img_bytes))
                except Exception as img_err:
                    logger.error(f"❌ PIL cannot identify image (frame {frame_count}). Bytes len: {len(img_bytes)}")
                    # Log a bit of the decoded bytes to see if it's a JPEG header
                    logger.debug(f"   Hex sample (first 16 bytes): {img_bytes[:16].hex()}")
                    raise

                # 5. Convert to RGB
                if image.mode != 'RGB':
                    image = image.convert('RGB')

                # 6. Process with YOLO (get raw detections)
                result = process_frame_yolo(model, image)
                
                # 7. Apply tracking and stabilization
                raw_detections = result["detections"]
                stable_detections = tracker.update(raw_detections)

                # Stats calculation
                total_processing_time += result["processing_time_ms"]
                avg_ms = total_processing_time / frame_count
                fps = 1000 / avg_ms if avg_ms > 0 else 0

                # 8. Build and send response
                response = {
                    "success": True,
                    "data": {
                        "detections": stable_detections,
                        "total_objects": len(stable_detections),
                        "frame_count": frame_count,
                        "stable": len(stable_detections) > 0,  # Stable if we have tracked objects
                    },
                    "metadata": {
                        "processing_time_ms": result["processing_time_ms"],
                        "average_processing_time_ms": round(avg_ms, 2),
                        "fps": round(fps, 2),
                        "image_size": result["image_size"],
                        "raw_detections": len(raw_detections),
                        "tracked_objects": len(tracker.tracked_objects)
                    }
                }
                await manager.broadcast_detection(response, db, tracker)

            except WebSocketDisconnect:
                raise
            except Exception as e:
                logger.error(f"❌ Error processing frame {frame_count}: {e}")
                try:
                    await websocket.send_json({
                        "success": False,
                        "error": str(e),
                        "frame_count": frame_count
                    })
                except:
                    break

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"🔌 Client disconnected. Frames: {frame_count}")
    except Exception as e:
        logger.error(f"💥 WebSocket crash: {e}")


@router.get("/realtime/status")
async def get_realtime_status():
    """
    Get real-time detection system status
    
    Returns:
        System status and configuration
    """
    try:
        model = get_model()
        
        return {
            "success": True,
            "status": "ready",
            "model_info": {
                "type": "YOLOv8s",
                "model_name": settings.MODEL_NAME,
                "num_classes": len(model.names),
                "class_names": list(model.names.values())
            },
            "configuration": {
                "confidence_threshold": settings.CONF_THRESHOLD,
                "iou_threshold": settings.IOU_THRESHOLD,
                "image_size": settings.IMAGE_SIZE
            },
            "capabilities": {
                "multiple_objects": True,
                "bounding_boxes": True,
                "realtime_processing": True
            }
        }
    
    except Exception as e:
        logger.error(f" Status check error: {e}")
        return {
            "success": False,
            "status": "error",
            "error": str(e)
        }


@router.post("/realtime/reset")
async def reset_realtime_detector():
    """
    Reset real-time detector
    
    Useful for clearing any cached state or statistics
    """
    logger.info(" Real-time detector reset requested")
    
    return {
        "success": True,
        "message": "Real-time detector reset successful",
        "timestamp": time.time()
    }


@router.post("/realtime/config")
async def update_realtime_config(
    confidence_threshold: float = None,
    iou_threshold: float = None
):
    """
    Update real-time detection configuration
    
    Args:
        confidence_threshold: New confidence threshold (0-1)
        iou_threshold: New IOU threshold (0-1)
    
    Returns:
        Updated configuration
    """
    try:
        # Validate thresholds
        if confidence_threshold is not None:
            if not 0 <= confidence_threshold <= 1:
                return {
                    "success": False,
                    "error": "Confidence threshold must be between 0 and 1"
                }
            settings.CONF_THRESHOLD = confidence_threshold
        
        if iou_threshold is not None:
            if not 0 <= iou_threshold <= 1:
                return {
                    "success": False,
                    "error": "IOU threshold must be between 0 and 1"
                }
            settings.IOU_THRESHOLD = iou_threshold
        
        return {
            "success": True,
            "message": "Configuration updated",
            "current_config": {
                "confidence_threshold": settings.CONF_THRESHOLD,
                "iou_threshold": settings.IOU_THRESHOLD
            }
        }
    
    except Exception as e:
        logger.error(f" Config update error: {e}")
        return {
            "success": False,
            "error": str(e)
        }