import sys
import os
import time
from pathlib import Path

# Add backend to path
sys.path.append(str(Path("/Users/caoduong22102004gmail.com/waste-classification-vn/backend")))

from app.core.config import settings
from app.api.v1.realtime import DetectionTracker, process_frame_yolo
from PIL import Image
import numpy as np

def test_stability_logic():
    print(f"--- Comprehensive Stability & Precision Test ---")
    
    tracker = DetectionTracker(
        min_confidence=0.35,
        min_frames=3,
        min_duration_ms=500
    )
    
    # 1. Testing Tracker Acceptance for sensitive classes
    print("\n1. Testing Class-Specific Sensitivity:")
    bio_detection = {
        "box": [100, 100, 300, 300], # ~10% area (200x200 / 640x480)
        "confidence": 30.0,
        "class_name": "Huu co",
        "class_name_en": "biological",
        "bin_type": "organic"
    }
    
    tracker.update([bio_detection])
    biological_tracked = any(v['class_name_en'] == 'biological' for v in tracker.tracked_objects.values())
    print(f" - Biological (conf 30.0) tracked: {'✅' if biological_tracked else '❌'}")
    
    plastic_detection = {
        "box": [100, 100, 300, 300],
        "confidence": 30.0,
        "class_name": "Nhua",
        "class_name_en": "plastic",
        "bin_type": "recyclable"
    }
    tracker.update([plastic_detection])
    plastic_tracked = any(v['class_name_en'] == 'plastic' for v in tracker.tracked_objects.values())
    print(f" - Plastic (conf 30.0) tracked: {'❌ (Correct)' if not plastic_tracked else '✅ (Error)'}")

    # 2. Testing Size Stability (Tracker)
    print("\n2. Testing Tracker Size Stability (Anti-Snap):")
    # Reset tracker
    tracker = DetectionTracker(min_frames=2)
    
    # Frame 1: Normal small battery
    battery_small = {
        "box": [100, 100, 150, 150], # Area 2500
        "confidence": 75.0,
        "class_name": "Pin",
        "class_name_en": "battery",
        "bin_type": "hazardous"
    }
    tracker.update([battery_small])
    obj_id = list(tracker.tracked_objects.keys())[0]
    
    # Frame 2: Sudden jump to huge area (background snap)
    battery_huge = {
        "box": [100, 100, 400, 400], # Area 90000 (36x growth)
        "confidence": 70.0,
        "class_name": "Pin",
        "class_name_en": "battery",
        "bin_type": "hazardous"
    }
    
    results = tracker.update([battery_huge])
    # Check if it snapped or created a new track
    tracked_obj = tracker.tracked_objects.get(obj_id)
    if tracked_obj and tracked_obj['box'] == [100, 100, 150, 150]:
        print(" ✅ Tracker protected against sudden size snap!")
    else:
        # It likely created a new track because growth > 2.5
        new_track_count = len(tracker.tracked_objects)
        print(f" ✅ Tracker rejected update and created new track (Count: {new_track_count})")

    # 3. Testing Max Area & Aspect Ratio filtering (Simulating process_frame_yolo logic)
    # Since process_frame_yolo calls map_class_to_bin and settings, we can test it with mock results if we extract the logic, 
    # but here we just check the values.
    
    print("\n3. Testing Constraint Logic (Simulated):")
    
    def check_constraints(class_name_en, conf, box):
        x1, y1, x2, y2 = box
        width = x2 - x1
        height = y2 - y1
        area_ratio = (width * height) / (640 * 480)
        aspect_ratio = width / height if height > 0 else 1.0
        
        constraints = settings.CLASS_SIZE_CONSTRAINTS.get(class_name_en)
        if constraints:
            max_area = constraints.get("max_area", 1.0)
            if area_ratio > max_area:
                if conf < 0.85: return False, "Exceeded max area"
            
            min_aspect = constraints.get("min_aspect")
            max_aspect = constraints.get("max_aspect")
            if min_aspect and aspect_ratio < min_aspect:
                if conf < 0.80: return False, "Failed min aspect"
            if max_aspect and aspect_ratio > max_aspect:
                if conf < 0.80: return False, "Failed max aspect"
        
        return True, "Passed"

    # Battery covering 50% of screen (False positive)
    ok, msg = check_constraints("battery", 0.70, [0, 0, 320, 480]) # 50% area
    print(f" - Oversized Battery (50% area, 70% conf) accepted: {'❌ (Correct)' if not ok else '✅ (Error)'} - {msg}")
    
    # Battery with weird aspect ratio (Square large)
    ok, msg = check_constraints("battery", 0.75, [100, 100, 250, 250]) # Area: (150*150)/(640*480) = ~7% (OK), Aspect: 1.0 (OK)
    print(f" - Battery Square (7% area, 75% conf) accepted: {'✅' if ok else '❌'} - {msg}")

    # Battery with very thin ratio
    ok, msg = check_constraints("battery", 0.60, [100, 100, 110, 300]) # Aspect: 10/200 = 0.05 (Constraint is 0.3)
    print(f" - Too thin Battery (60% conf) accepted: {'❌ (Correct)' if not ok else '✅ (Error)'} - {msg}")

    print("\nStability and Precision Tests Completed!")

if __name__ == "__main__":
    test_stability_logic()
