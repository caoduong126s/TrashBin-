"""
Result Smoothing Service - FIXED VERSION
Uses Counter instead of scipy.stats.mode for string data
"""

import numpy as np
from collections import deque, Counter
from typing import Optional, Tuple, Dict, Any

class ResultSmoother:
    """
    Smooths classification results over time to prevent flickering
    Uses voting mechanism to ensure stable predictions
    """
    
    def __init__(self, window_size: int = 8, stability_threshold: float = 0.6):
        """
        Initialize result smoother
        
        Args:
            window_size: Number of recent predictions to consider
            stability_threshold: Minimum frequency (0-1) for stable result
        """
        self.window_size = window_size
        self.stability_threshold = stability_threshold
        
        # History buffers
        self.class_history = deque(maxlen=window_size)
        self.confidence_history = deque(maxlen=window_size)
        self.bin_history = deque(maxlen=window_size)
        
        # State
        self.stable_result = None
        self.frames_stable = 0
        
    def add_prediction(
        self,
        class_name: str,
        confidence: float,
        bin_type: str
    ) -> None:
        """
        Add a new prediction to history
        
        Args:
            class_name: Predicted waste class
            confidence: Confidence score (0-100)
            bin_type: Bin type (recyclable/general/hazardous)
        """
        self.class_history.append(class_name)
        self.confidence_history.append(confidence)
        self.bin_history.append(bin_type)
    
    def get_stable_result(self) -> Optional[Dict[str, Any]]:
        """
        Get stable prediction if confidence is high enough
        
        Returns:
            Stable result dict or None if not stable yet
        """
        if len(self.class_history) < 3:
            # Not enough data yet
            return None
        
        # Find most common class using Counter
        counter = Counter(self.class_history)
        most_common_class, occurrence_count = counter.most_common(1)[0]
        
        # Calculate frequency
        frequency = occurrence_count / len(self.class_history)
        
        # Check if stable enough
        if frequency >= self.stability_threshold:
            # Get average confidence for this class
            class_confidences = [
                conf for cls, conf in zip(self.class_history, self.confidence_history)
                if cls == most_common_class
            ]
            avg_confidence = np.mean(class_confidences)
            
            # Get bin type (should be consistent)
            class_bins = [
                bin_type for cls, bin_type in zip(self.class_history, self.bin_history)
                if cls == most_common_class
            ]
            bin_counter = Counter(class_bins)
            bin_mode = bin_counter.most_common(1)[0][0]
            
            # Create stable result
            stable_result = {
                'class_name': most_common_class,
                'confidence': avg_confidence,
                'bin_type': bin_mode,
                'frequency': frequency,
                'sample_size': len(self.class_history),
                'stable': True
            }
            
            # Track stability
            if self.stable_result and self.stable_result['class_name'] == most_common_class:
                self.frames_stable += 1
            else:
                self.frames_stable = 1
            
            self.stable_result = stable_result
            stable_result['frames_stable'] = self.frames_stable
            
            return stable_result
        
        # Not stable yet
        return None
    
    def get_latest_prediction(self) -> Optional[Dict[str, Any]]:
        """
        Get most recent prediction (even if not stable)
        
        Returns:
            Latest prediction or None
        """
        if not self.class_history:
            return None
        
        return {
            'class_name': self.class_history[-1],
            'confidence': self.confidence_history[-1],
            'bin_type': self.bin_history[-1],
            'stable': False
        }
    
    def get_stability_score(self) -> float:
        """
        Get current stability score (0-1)
        Higher = more stable
        
        Returns:
            Stability score
        """
        if len(self.class_history) < 2:
            return 0.0
        
        # Calculate how often predictions agree
        counter = Counter(self.class_history)
        most_common_count = counter.most_common(1)[0][1]
        frequency = most_common_count / len(self.class_history)
        
        return float(frequency)
    
    def get_progress(self) -> Tuple[int, int]:
        """
        Get progress toward stable result
        
        Returns:
            (current_frames, min_required_frames)
        """
        min_required = max(3, int(self.window_size * self.stability_threshold))
        return (len(self.class_history), min_required)
    
    def reset(self):
        """Reset all history"""
        self.class_history.clear()
        self.confidence_history.clear()
        self.bin_history.clear()
        self.stable_result = None
        self.frames_stable = 0
    
    def is_building_confidence(self) -> bool:
        """Check if still building confidence"""
        return len(self.class_history) > 0 and self.get_stable_result() is None


def test_smoother():
    """Test result smoother with simulated predictions"""
    print(" Testing Result Smoother\n")
    
    smoother = ResultSmoother(window_size=8, stability_threshold=0.6)
    
    # Simulate predictions with some noise
    test_predictions = [
        ('Nhựa', 95.0, 'recyclable'),
        ('Nhựa', 93.0, 'recyclable'),
        ('Giấy', 85.0, 'recyclable'),  # Noise
        ('Nhựa', 96.0, 'recyclable'),
        ('Nhựa', 94.0, 'recyclable'),
        ('Nhựa', 97.0, 'recyclable'),
        ('Kim loại', 82.0, 'recyclable'),  # Noise
        ('Nhựa', 95.0, 'recyclable'),
        ('Nhựa', 96.0, 'recyclable'),
        ('Nhựa', 94.0, 'recyclable'),
    ]
    
    for i, (class_name, conf, bin_type) in enumerate(test_predictions, 1):
        smoother.add_prediction(class_name, conf, bin_type)
        
        stable = smoother.get_stable_result()
        latest = smoother.get_latest_prediction()
        stability = smoother.get_stability_score()
        progress = smoother.get_progress()
        
        print(f"Frame {i:2d}:")
        print(f"  Latest:  {latest['class_name']:10s} ({latest['confidence']:.1f}%)")
        
        if stable:
            print(f"   STABLE: {stable['class_name']:10s} ({stable['confidence']:.1f}%)")
            print(f"  Frequency: {stable['frequency']:.1%}")
            print(f"  Frames stable: {stable['frames_stable']}")
        else:
            print(f"   Building confidence... ({progress[0]}/{progress[1]})")
            print(f"  Stability: {stability:.1%}")
        
        print()
    
    print("=" * 50)
    print(" Test Complete!")
    print(f"Final result: {smoother.get_stable_result()}")

if __name__ == "__main__":
    test_smoother()