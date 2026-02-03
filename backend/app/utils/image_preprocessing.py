"""
Image Preprocessing for Low-Light Enhancement
Automatically detects and enhances images taken in dark conditions
"""

import cv2
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)


def calculate_brightness(image_np: np.ndarray) -> float:
    """
    Calculate average brightness of an image
    
    Args:
        image_np: Numpy array of image (RGB or BGR)
        
    Returns:
        Average brightness (0-255)
    """
    # Convert to grayscale
    if len(image_np.shape) == 3:
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    else:
        gray = image_np
    
    # Calculate mean brightness
    brightness = np.mean(gray)
    return float(brightness)


def is_low_light(image_np: np.ndarray, threshold: float = 80.0) -> bool:
    """
    Detect if image is taken in low-light conditions
    
    Args:
        image_np: Numpy array of image
        threshold: Brightness threshold (default: 80)
        
    Returns:
        True if image is dark
    """
    brightness = calculate_brightness(image_np)
    return brightness < threshold


def enhance_brightness_adaptive(image_np: np.ndarray) -> np.ndarray:
    """
    Adaptively enhance image brightness using CLAHE
    (Contrast Limited Adaptive Histogram Equalization)
    
    Args:
        image_np: Input image (RGB)
        
    Returns:
        Enhanced image (RGB)
    """
    # Convert RGB to LAB color space
    lab = cv2.cvtColor(image_np, cv2.COLOR_RGB2LAB)
    
    # Split LAB channels
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    
    # Merge channels
    lab_enhanced = cv2.merge([l_enhanced, a, b])
    
    # Convert back to RGB
    enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2RGB)
    
    return enhanced


def enhance_brightness_gamma(image_np: np.ndarray, gamma: float = 1.5) -> np.ndarray:
    """
    Enhance brightness using gamma correction
    
    Args:
        image_np: Input image (RGB)
        gamma: Gamma value (> 1 brightens, < 1 darkens)
        
    Returns:
        Enhanced image (RGB)
    """
    # Build lookup table
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
    
    # Apply gamma correction
    enhanced = cv2.LUT(image_np, table)
    
    return enhanced


def auto_enhance_low_light(
    image_np: np.ndarray,
    method: str = "clahe",
    brightness_threshold: float = 80.0,
    force: bool = False
) -> tuple[np.ndarray, bool, dict]:
    """
    Automatically enhance image if it's taken in low-light conditions
    
    Args:
        image_np: Input image (RGB numpy array)
        method: Enhancement method ("clahe", "gamma", or "both")
        brightness_threshold: Threshold to detect low-light
        force: Force enhancement regardless of brightness
        
    Returns:
        Tuple of (enhanced_image, was_enhanced, metadata)
    """
    metadata = {}
    
    # Calculate original brightness
    original_brightness = calculate_brightness(image_np)
    metadata["original_brightness"] = round(original_brightness, 2)
    metadata["brightness_threshold"] = brightness_threshold
    
    # Check if enhancement is needed
    needs_enhancement = force or is_low_light(image_np, brightness_threshold)
    metadata["is_low_light"] = needs_enhancement
    
    if not needs_enhancement:
        metadata["enhanced"] = False
        metadata["method"] = None
        return image_np, False, metadata
    
    # Apply enhancement
    logger.info(f" Low-light detected (brightness: {original_brightness:.1f}), applying enhancement...")
    
    if method == "clahe":
        enhanced = enhance_brightness_adaptive(image_np)
    elif method == "gamma":
        enhanced = enhance_brightness_gamma(image_np, gamma=1.5)
    elif method == "both":
        # Apply both methods sequentially
        enhanced = enhance_brightness_gamma(image_np, gamma=1.2)
        enhanced = enhance_brightness_adaptive(enhanced)
    else:
        logger.warning(f"Unknown enhancement method: {method}, using CLAHE")
        enhanced = enhance_brightness_adaptive(image_np)
    
    # Calculate new brightness
    new_brightness = calculate_brightness(enhanced)
    metadata["enhanced_brightness"] = round(new_brightness, 2)
    metadata["brightness_improvement"] = round(new_brightness - original_brightness, 2)
    metadata["enhanced"] = True
    metadata["method"] = method
    
    logger.info(f" Enhancement complete: {original_brightness:.1f} → {new_brightness:.1f} (+{new_brightness - original_brightness:.1f})")
    
    return enhanced, True, metadata


def preprocess_image_for_detection(
    image: Image.Image,
    enable_low_light_mode: bool = True,
    low_light_method: str = "clahe",
    brightness_threshold: float = 80.0
) -> tuple[Image.Image, dict]:
    """
    Preprocess PIL Image for YOLO detection
    
    Args:
        image: PIL Image
        enable_low_light_mode: Enable automatic low-light enhancement
        low_light_method: Enhancement method
        brightness_threshold: Brightness threshold
        
    Returns:
        Tuple of (processed_image, metadata)
    """
    # Convert PIL to numpy
    image_np = np.array(image)
    
    metadata = {"preprocessing_applied": []}
    
    # Apply low-light enhancement if enabled
    if enable_low_light_mode:
        enhanced_np, was_enhanced, enhance_meta = auto_enhance_low_light(
            image_np,
            method=low_light_method,
            brightness_threshold=brightness_threshold
        )
        
        if was_enhanced:
            image_np = enhanced_np
            metadata["preprocessing_applied"].append("low_light_enhancement")
        
        metadata["low_light"] = enhance_meta
    else:
        metadata["low_light"] = {"enabled": False}
    
    # Convert back to PIL
    processed_image = Image.fromarray(image_np)
    
    return processed_image, metadata
