"""
Motion Detection Service
Detects when frame has changed significantly to trigger inference
"""

import cv2
import numpy as np
from typing import Optional, Tuple

class MotionDetector:
    """
    Detects motion between frames to avoid unnecessary inference
    """
    
    def __init__(
        self,
        threshold: int = 25,
        min_area: int = 5000,
        blur_size: int = 21
    ):
        """
        Initialize motion detector
        
        Args:
            threshold: Pixel difference threshold (0-255)
            min_area: Minimum changed pixels to consider motion
            blur_size: Gaussian blur kernel size (must be odd)
        """
        self.threshold = threshold
        self.min_area = min_area
        self.blur_size = blur_size
        self.prev_frame = None
        self.motion_history = []
        
    def detect(self, frame: np.ndarray) -> Tuple[bool, float]:
        """
        Detect if frame has significant motion
        
        Args:
            frame: BGR image from camera
            
        Returns:
            (has_motion, motion_score): Boolean and motion intensity 0-1
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        gray = cv2.GaussianBlur(gray, (self.blur_size, self.blur_size), 0)
        
        # First frame - no previous to compare
        if self.prev_frame is None:
            self.prev_frame = gray
            return True, 1.0
        
        # Compute absolute difference
        frame_delta = cv2.absdiff(self.prev_frame, gray)
        
        # Threshold the delta
        thresh = cv2.threshold(frame_delta, self.threshold, 255, cv2.THRESH_BINARY)[1]
        
        # Dilate to fill gaps
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Count changed pixels
        motion_pixels = np.sum(thresh) / 255
        
        # Calculate motion score (0-1)
        motion_score = min(motion_pixels / self.min_area, 1.0)
        
        # Update previous frame
        self.prev_frame = gray
        
        # Add to history
        self.motion_history.append(motion_score)
        if len(self.motion_history) > 30:  # Keep last 30 frames
            self.motion_history.pop(0)
        
        # Determine if there's motion
        has_motion = motion_pixels > self.min_area
        
        return has_motion, motion_score
    
    def get_average_motion(self) -> float:
        """Get average motion over recent frames"""
        if not self.motion_history:
            return 0.0
        return np.mean(self.motion_history)
    
    def is_stable(self, stability_threshold: float = 0.1) -> bool:
        """Check if scene is stable (low motion)"""
        avg_motion = self.get_average_motion()
        return avg_motion < stability_threshold
    
    def reset(self):
        """Reset detector state"""
        self.prev_frame = None
        self.motion_history = []

def test_motion_detector():
    """Test motion detection with webcam"""
    print(" Testing Motion Detector (Press 'q' to quit)")
    
    cap = cv2.VideoCapture(0)
    detector = MotionDetector(threshold=25, min_area=5000)
    
    frame_count = 0
    motion_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Detect motion
        has_motion, motion_score = detector.detect(frame)
        
        if has_motion:
            motion_count += 1
        
        # Draw status
        status_text = f"Motion: {'YES' if has_motion else 'NO'} ({motion_score:.2f})"
        status_color = (0, 255, 0) if has_motion else (128, 128, 128)
        
        cv2.putText(
            frame, status_text, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2
        )
        
        # Draw stats
        stats_text = f"Frames: {frame_count} | Motion: {motion_count} ({motion_count/frame_count*100:.1f}%)"
        cv2.putText(
            frame, stats_text, (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
        )
        
        # Show frame
        cv2.imshow('Motion Detection Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n Results:")
    print(f"   Total frames: {frame_count}")
    print(f"   Motion frames: {motion_count}")
    print(f"   Motion ratio: {motion_count/frame_count*100:.1f}%")
    print(f"   Inference saved: {(frame_count - motion_count)/frame_count*100:.1f}%")

if __name__ == "__main__":
    test_motion_detector()
