"""
Test script for realtime YOLO detection with webcam
Connects to WebSocket endpoint and streams camera frames
"""

import cv2
import asyncio
import websockets
import json
import base64
from pathlib import Path

# WebSocket URL
WS_URL = "ws://127.0.0.1:8000/api/v1/ws/realtime-detect"

# Colors for different bin types
BIN_COLORS = {
    "recyclable": (0, 255, 0),      # Green
    "organic": (0, 165, 255),       # Orange
    "hazardous": (0, 0, 255),       # Red
    "general": (128, 128, 128)      # Gray
}

def draw_detections(frame, detections):
    """Draw bounding boxes and labels on frame"""
    for detection in detections:
        box = detection["box"]
        x1, y1, x2, y2 = box
        
        # Get color based on bin type
        bin_type = detection.get("bin_type", "general")
        color = BIN_COLORS.get(bin_type, (255, 255, 255))
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Prepare label - use English to avoid OpenCV Unicode issues
        class_name_en = detection.get("class_name_en", detection["class_name"])
        confidence = detection["confidence"]
        label = f"{class_name_en} {confidence:.1f}%"
        
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
    
    return frame

async def test_realtime_camera():
    """Main function to test realtime camera detection"""
    print("=" * 60)
    print(" YOLO Realtime Camera Test")
    print("=" * 60)
    print(f"Connecting to: {WS_URL}")
    print("Press 'q' to quit")
    print("=" * 60)
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print(" Error: Could not open webcam")
        return
    
    print(" Webcam opened successfully")
    
    # Set camera resolution (optional)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print(" Connected to WebSocket server")
            
            frame_count = 0
            
            while True:
                # Capture frame
                ret, frame = cap.read()
                
                if not ret:
                    print(" Error: Could not read frame")
                    break
                
                frame_count += 1
                
                # Encode frame to JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                
                # Convert to base64
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Send frame to server
                await websocket.send(frame_base64)
                
                # Receive response
                response_str = await websocket.recv()
                response = json.loads(response_str)
                
                if response.get("success"):
                    data = response["data"]
                    detections = data["detections"]
                    total_objects = data["total_objects"]
                    
                    # Draw detections on frame
                    frame = draw_detections(frame, detections)
                    
                    # Draw info overlay
                    info_text = f"Frame: {frame_count} | Objects: {total_objects}"
                    cv2.putText(
                        frame,
                        info_text,
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )
                    
                    # Show metadata if available
                    if "metadata" in response:
                        meta = response["metadata"]
                        fps_text = f"FPS: {meta.get('fps', 0):.1f} | Time: {meta.get('processing_time_ms', 0):.1f}ms"
                        cv2.putText(
                            frame,
                            fps_text,
                            (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 255),
                            2
                        )
                    
                    # Print detection summary
                    if total_objects > 0 and frame_count % 30 == 0:  # Print every 30 frames
                        print(f"Frame {frame_count}: Detected {total_objects} objects")
                        for det in detections[:3]:  # Show first 3
                            print(f"  - {det['class_name']}: {det['confidence']:.1f}%")
                
                else:
                    error = response.get("error", "Unknown error")
                    cv2.putText(
                        frame,
                        f"Error: {error}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 0, 255),
                        2
                    )
                
                # Display frame
                cv2.imshow('YOLO Realtime Detection', frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n Quitting...")
                    break
    
    except websockets.exceptions.ConnectionClosed:
        print(" WebSocket connection closed")
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        print("\n Camera released and windows closed")

if __name__ == "__main__":
    print("\n Starting YOLO Realtime Camera Test...")
    print("Make sure the backend server is running at http://127.0.0.1:8000")
    print()
    
    try:
        asyncio.run(test_realtime_camera())
    except KeyboardInterrupt:
        print("\n\n Test interrupted by user")
    
    print("\n Test completed")
