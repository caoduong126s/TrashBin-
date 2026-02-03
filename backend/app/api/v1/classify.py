"""
Classification Endpoint - YOLO Version
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from PIL import Image
import io
import logging
import numpy as np
from typing import Dict, List
import time

from app.core.config import settings
from app.core.database import get_db
from app.core.model_loader import get_model
from app.models.classification import ClassificationHistory
from app.utils.image_preprocessing import preprocess_image_for_detection
from app.utils.bin_mapping import map_class_to_bin, BinType

router = APIRouter()
logger = logging.getLogger(__name__)


def get_bin_type(class_name_en: str) -> str:
    """
    Get bin type from English class name using proper mapping
    
    Args:
        class_name_en: English class name (e.g., 'plastic', 'battery')
        
    Returns:
        Bin type string ('recyclable', 'general', 'hazardous')
    """
    bin_type_enum = map_class_to_bin(class_name_en)
    return bin_type_enum.value


def validate_image(file: UploadFile) -> None:
    """
    Validate uploaded image
    
    Args:
        file: Uploaded file
        
    Raises:
        HTTPException: If validation fails
    """
    # Check file extension
    file_ext = f".{file.filename.split('.')[-1].lower()}"
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Định dạng file không hợp lệ. Chỉ chấp nhận: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Check content type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File không phải là ảnh hợp lệ"
        )


def classify_image_yolo(image: Image.Image) -> Dict:
    """
    Classify image using YOLO model with low-light enhancement
    
    Args:
        image: PIL Image
        
    Returns:
        Detection results with boxes and classes
    """
    start_time = time.time()
    
    # Apply low-light preprocessing if enabled
    preprocessing_metadata = {}
    if settings.ENABLE_LOW_LIGHT_MODE:
        image, preprocessing_metadata = preprocess_image_for_detection(
            image,
            enable_low_light_mode=True,
            low_light_method=settings.LOW_LIGHT_METHOD,
            brightness_threshold=settings.LOW_LIGHT_BRIGHTNESS_THRESHOLD
        )
    
    # Get YOLO model
    model = get_model()
    
    # Convert PIL to numpy array (RGB)
    image_np = np.array(image)
    
    # Run YOLO prediction with error handling
    try:
        results = model.predict(
            source=image_np,
            conf=settings.CONF_THRESHOLD,
            iou=settings.IOU_THRESHOLD,
            imgsz=settings.IMAGE_SIZE,
            verbose=False
        )
    except Exception as e:
        logger.error(f"❌ YOLO prediction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Model prediction failed: {str(e)}"
        )
    
    # Parse results
    detections = []
    result = results[0]  # Get first result (single image)
    
    if result.boxes is not None and len(result.boxes) > 0:
        boxes = result.boxes
        
        for idx, box in enumerate(boxes):
            # Get box coordinates
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            
            # Get confidence and class
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            
            # Validate class index is within bounds
            if cls < 0 or cls >= len(result.names):
                logger.warning(f"⚠️  Invalid class index {cls}, skipping detection")
                continue
            
            # Get class name from model (Vietnamese)
            class_name_vn = result.names[cls]  # Model returns Vietnamese names
            
            # Convert to English for bin mapping
            from app.utils.bin_mapping import VN_TO_EN_CLASS_NAMES
            class_name_en = VN_TO_EN_CLASS_NAMES.get(class_name_vn, class_name_vn.lower())
            
            # Get bin type using the class name (supports both VN and EN)
            bin_type = get_bin_type(class_name_vn)
            
            # Create detection object
            detection = {
                "box": [int(x1), int(y1), int(x2), int(y2)],
                "confidence": round(conf, 3),  # Consistent 3 decimal places
                "class_name": class_name_vn,  # Vietnamese for display
                "class_name_en": class_name_en,  # English for reference
                "bin_type": bin_type,
                "detection_id": idx
            }
            
            detections.append(detection)
    
    processing_time = time.time() - start_time
    
    # Sort detections by confidence (highest first)
    detections.sort(key=lambda x: x["confidence"], reverse=True)
    
    result_dict = {
        "detections": detections,
        "total_objects": len(detections),
        "processing_time": round(processing_time, 3),
        "image_size": {
            "width": image.width,
            "height": image.height
        }
    }
    
    # Add preprocessing metadata if available
    if preprocessing_metadata:
        result_dict["preprocessing"] = preprocessing_metadata
    
    return result_dict


@router.post("/classify")
async def classify_waste(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Classify waste image using YOLO object detection
    
    Args:
        file: Uploaded image file
        db: Database session
        
    Returns:
        Detection results with bounding boxes
    """
    try:
        # Validate file
        validate_image(file)
        
        # Read image
        contents = await file.read()
        
        # Check file size
        if len(contents) > settings.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File quá lớn. Kích thước tối đa: {settings.MAX_IMAGE_SIZE / 1024 / 1024:.1f}MB"
            )
        
        # Open image
        try:
            image = Image.open(io.BytesIO(contents))
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Không thể đọc file ảnh: {str(e)}"
            )
        
        # Run YOLO detection
        result = classify_image_yolo(image)
        
        # Save detections to database
        if result["total_objects"] > 0:
            try:
                # Save each detection
                for detection in result["detections"]:
                    history = ClassificationHistory(
                        class_name=detection["class_name_en"],
                        class_name_vn=detection["class_name"],
                        confidence=detection["confidence"],
                        bin_type=detection["bin_type"],
                        processing_time=result["processing_time"],
                        user_id="anonymous",
                        # Store box coordinates (if your table supports it)
                        # box_x1=detection["box"][0],
                        # box_y1=detection["box"][1],
                        # box_x2=detection["box"][2],
                        # box_y2=detection["box"][3],
                    )
                    
                    db.add(history)
                
                db.commit()
                logger.info(f" Saved {result['total_objects']} detections to database")
                
            except Exception as db_error:
                logger.error(f" Failed to save to database: {db_error}")
                db.rollback()
                logger.warning("  Detection results returned but not saved")
        else:
            logger.info("ℹ  No objects detected")
        
        # Return response
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi phân loại ảnh: {str(e)}"
        )


@router.post("/classify/single")
async def classify_waste_single(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Legacy endpoint: Returns only the highest confidence detection
    For backward compatibility with old frontend code
    
    Args:
        file: Uploaded image file
        db: Database session
        
    Returns:
        Single classification result (highest confidence)
    """
    try:
        # Use the main classify endpoint
        result = await classify_waste(file, db)
        
        if not result["success"] or result["data"]["total_objects"] == 0:
            return {
                "success": False,
                "data": {
                    "class_name": "unknown",
                    "confidence": 0.0,
                    "bin_type": "general",
                    "message": "Không phát hiện vật thể nào"
                }
            }
        
        # Get highest confidence detection
        best_detection = result["data"]["detections"][0]
        
        # Return in old format
        return {
            "success": True,
            "data": {
                "class_name": best_detection["class_name"],
                "class_name_en": best_detection["class_name_en"],
                "confidence": best_detection["confidence"],
                "bin_type": best_detection["bin_type"],
                "processing_time": result["data"]["processing_time"],
                "box": best_detection["box"]  # Include box for reference
            }
        }
        
    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi phân loại ảnh: {str(e)}"
        )