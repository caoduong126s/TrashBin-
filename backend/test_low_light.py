"""
Test script for low-light mode preprocessing
Tests image enhancement on dark images
"""

import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import sys

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.utils.image_preprocessing import (
    calculate_brightness,
    is_low_light,
    enhance_brightness_adaptive,
    enhance_brightness_gamma,
    auto_enhance_low_light,
    preprocess_image_for_detection
)

def create_dark_test_image(output_path: Path):
    """Create a dark test image for testing"""
    # Create a dark image with some colored shapes
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Add some dim colored rectangles
    cv2.rectangle(img, (50, 50), (200, 200), (40, 40, 80), -1)  # Dark blue
    cv2.rectangle(img, (250, 100), (400, 250), (60, 80, 40), -1)  # Dark green
    cv2.rectangle(img, (450, 150), (590, 300), (80, 40, 40), -1)  # Dark red
    
    # Add some text (barely visible)
    cv2.putText(img, "Low Light Test", (200, 400), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (80, 80, 80), 2)
    
    # Save
    cv2.imwrite(str(output_path), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    print(f" Created dark test image at: {output_path}")
    
    return img

def test_low_light_detection():
    """Test low-light detection"""
    print("\n" + "=" * 60)
    print("Testing Low-Light Detection")
    print("=" * 60)
    
    # Create dark and bright images
    dark_img = np.ones((100, 100, 3), dtype=np.uint8) * 50  # Dark
    bright_img = np.ones((100, 100, 3), dtype=np.uint8) * 150  # Bright
    
    dark_brightness = calculate_brightness(dark_img)
    bright_brightness = calculate_brightness(bright_img)
    
    print(f"\nDark image brightness: {dark_brightness:.1f}")
    print(f"Dark image is low-light: {is_low_light(dark_img)}")
    
    print(f"\nBright image brightness: {bright_brightness:.1f}")
    print(f"Bright image is low-light: {is_low_light(bright_img)}")

def test_enhancement_methods():
    """Test different enhancement methods"""
    print("\n" + "=" * 60)
    print("Testing Enhancement Methods")
    print("=" * 60)
    
    # Create test image
    test_dir = Path(__file__).parent / "test_images"
    test_dir.mkdir(exist_ok=True)
    
    dark_img_path = test_dir / "dark_test.jpg"
    dark_img = create_dark_test_image(dark_img_path)
    
    print(f"\nOriginal brightness: {calculate_brightness(dark_img):.1f}")
    
    # Test CLAHE
    print("\n1. Testing CLAHE enhancement...")
    enhanced_clahe = enhance_brightness_adaptive(dark_img)
    clahe_brightness = calculate_brightness(enhanced_clahe)
    print(f"   CLAHE brightness: {clahe_brightness:.1f}")
    cv2.imwrite(str(test_dir / "enhanced_clahe.jpg"), 
                cv2.cvtColor(enhanced_clahe, cv2.COLOR_RGB2BGR))
    
    # Test Gamma
    print("\n2. Testing Gamma enhancement...")
    enhanced_gamma = enhance_brightness_gamma(dark_img, gamma=1.5)
    gamma_brightness = calculate_brightness(enhanced_gamma)
    print(f"   Gamma brightness: {gamma_brightness:.1f}")
    cv2.imwrite(str(test_dir / "enhanced_gamma.jpg"), 
                cv2.cvtColor(enhanced_gamma, cv2.COLOR_RGB2BGR))
    
    # Test Auto
    print("\n3. Testing Auto enhancement...")
    enhanced_auto, was_enhanced, metadata = auto_enhance_low_light(
        dark_img, method="clahe"
    )
    print(f"   Was enhanced: {was_enhanced}")
    print(f"   Metadata: {metadata}")
    cv2.imwrite(str(test_dir / "enhanced_auto.jpg"), 
                cv2.cvtColor(enhanced_auto, cv2.COLOR_RGB2BGR))
    
    print(f"\n Enhanced images saved to: {test_dir}")

def test_full_preprocessing():
    """Test full preprocessing pipeline"""
    print("\n" + "=" * 60)
    print("Testing Full Preprocessing Pipeline")
    print("=" * 60)
    
    # Create test image
    test_dir = Path(__file__).parent / "test_images"
    test_dir.mkdir(exist_ok=True)
    
    dark_img_path = test_dir / "dark_test.jpg"
    if not dark_img_path.exists():
        create_dark_test_image(dark_img_path)
    
    # Load as PIL
    pil_image = Image.open(dark_img_path)
    
    # Test with low-light mode enabled
    print("\n1. With low-light mode enabled:")
    processed, metadata = preprocess_image_for_detection(
        pil_image,
        enable_low_light_mode=True,
        low_light_method="clahe",
        brightness_threshold=80.0
    )
    print(f"   Metadata: {metadata}")
    processed.save(test_dir / "preprocessed_enabled.jpg")
    
    # Test with low-light mode disabled
    print("\n2. With low-light mode disabled:")
    processed, metadata = preprocess_image_for_detection(
        pil_image,
        enable_low_light_mode=False
    )
    print(f"   Metadata: {metadata}")
    
    print(f"\n Preprocessing test complete")

if __name__ == "__main__":
    print("\n Testing Low-Light Mode Preprocessing")
    print("=" * 60)
    
    try:
        test_low_light_detection()
        test_enhancement_methods()
        test_full_preprocessing()
        
        print("\n" + "=" * 60)
        print(" All tests completed successfully!")
        print("=" * 60)
        print("\nCheck the 'test_images' folder for visual comparison")
        
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
