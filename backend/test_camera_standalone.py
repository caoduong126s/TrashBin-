"""
Standalone YOLO Camera Test - No server required
Tests YOLO model directly with webcam
"""

import cv2
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.core.model_loader import get_model
from app.core.config import settings

# Colors for different bin types
BIN_COLORS = {
    "recyclable": (0, 255, 0),      # Green
    "organic": (0, 165, 255),       # Orange
    "hazardous": (0, 0, 255),       # Red
    "general": (128, 128, 128)      # Gray
}

BIN_TYPE_MAPPING = {
    "Nhựa": "recyclable",
    "Giấy": "recyclable",
    "Hộp giấy": "recyclable",
    "Kim loại": "recyclable",
    "Thủy tinh": "recyclable",
    "Vải": "recyclable",
    "Hữu cơ": "organic",
    "Pin": "hazardous",
    "Rác thải": "general"
}

def get_bin_type(class_name_vn):
    """Get bin type from Vietnamese class name"""
    return BIN_TYPE_MAPPING.get(class_name_vn, "general")

def draw_detections(frame, results):
    """Draw bounding boxes and labels on frame"""
    if results[0].boxes is None or len(results[0].boxes) == 0:
        return frame, 0
    
    boxes = results[0].boxes
    count = 0
    
    for box in boxes:
        # Get box coordinates
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        
        # Get confidence and class
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        
        # Get class name (English only to avoid OpenCV Unicode issues)
        class_name_en = results[0].names[cls]
        
        # Get bin type from English class name
        bin_type = map_class_to_bin(class_name_en).value
        color = BIN_COLORS.get(bin_type, (255, 255, 255))
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Prepare label with English class name (no Vietnamese to avoid encoding issues)
        label = f"{class_name_en} {conf*100:.1f}%"
        
        # Draw label background
        (label_width, label_height), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
        )
        cv2.rectangle(
            frame,
            (x1, y1 - label_height - 10),
            (x1 + label_width, y1),
            color,
            -1
        )
        
        # Draw label text
        cv2.putText(
            frame,
            label,
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )
        
        count += 1
    
    return frame, count

def main():
    """Main function"""
    print("=" * 60)
    print(" YOLO Camera Test (Standalone)")
    print("=" * 60)
    print("Loading YOLO model...")
    
    # Load model
    try:
        model = get_model()
        print(f" Model loaded: {len(model.names)} classes")
        print(f"   Confidence threshold: {settings.CONF_THRESHOLD}")
        print(f"   IOU threshold: {settings.IOU_THRESHOLD}")
    except Exception as e:
        print(f" Failed to load model: {e}")
        return
    
    print("\nOpening webcam...")
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print(" Error: Could not open webcam")
        return
    
    print(" Webcam opened successfully")
    print("\n" + "=" * 60)
    print("Controls:")
    print("  - Press 'q' to quit")
    print("  - Show objects to the camera to detect them")
    print("=" * 60 + "\n")
    
    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    frame_count = 0
    
    try:
        while True:
            # Capture frame
            ret, frame = cap.read()
            
            if not ret:
                print(" Error: Could not read frame")
                break
            
            frame_count += 1
            
            # Run YOLO detection
            results = model.predict(
                source=frame,
                conf=settings.CONF_THRESHOLD,
                iou=settings.IOU_THRESHOLD,
                imgsz=settings.IMAGE_SIZE,
                verbose=False
            )
            
            # Draw detections
            frame, num_objects = draw_detections(frame, results)
            
            # Draw info overlay
            info_text = f"Frame: {frame_count} | Objects: {num_objects}"
            cv2.putText(
                frame,
                info_text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
            
            # Print detection info every 30 frames
            if num_objects > 0 and frame_count % 30 == 0:
                print(f"Frame {frame_count}: Detected {num_objects} objects")
                boxes = results[0].boxes
                for i, box in enumerate(boxes[:3]):  # Show first 3
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name_en = results[0].names[cls]
                    class_name_vn = settings.CLASS_NAMES_VN.get(class_name_en, class_name_en)
                    print(f"  - {class_name_vn}: {conf*100:.1f}%")
            
            # Display frame
            cv2.imshow('YOLO Detection - Press Q to quit', frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n Quitting...")
                break
    
    except KeyboardInterrupt:
        print("\n\n Interrupted by user")
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        print("\n Camera released and windows closed")

if __name__ == "__main__":
    print("\n Starting YOLO Camera Test...")
    print("This script runs independently - no server needed!\n")
    
    main()
    
    print("\n Test completed")
