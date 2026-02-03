import cv2
import numpy as np
import os
import random
from pathlib import Path
import matplotlib.pyplot as plt

def apply_hsv_jitter(image):
    """Apply HSV color space jitter"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    
    # Randomly shift H, S, V
    hsv[:, :, 0] = (hsv[:, :, 0] + random.uniform(-10, 10)) % 180
    hsv[:, :, 1] *= random.uniform(0.5, 1.5)
    hsv[:, :, 2] *= random.uniform(0.5, 1.5)
    
    hsv = np.clip(hsv, 0, 255).astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def apply_geometric(image):
    """Apply random rotation and flip"""
    h, w = image.shape[:2]
    # Rotation
    angle = random.uniform(-30, 30)
    M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REFLECT)
    
    # Horizontal flip
    if random.random() > 0.5:
        rotated = cv2.flip(rotated, 1)
        
    return rotated

def create_mosaic(images, size=(640, 640)):
    """Create a 4-image Mosaic augmentation"""
    if len(images) < 4:
        # Pad with copies if not enough images
        images = images * 4
        
    h, w = size
    # Create canvas
    mosaic = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Center points for 4 images
    yc, xc = h // 2, w // 2
    
    for i in range(4):
        img = cv2.resize(images[i], (xc, yc))
        if i == 0: # Top-left
            mosaic[0:yc, 0:xc] = img
        elif i == 1: # Top-right
            mosaic[0:yc, xc:w] = img
        elif i == 2: # Bottom-left
            mosaic[yc:h, 0:xc] = img
        elif i == 3: # Bottom-right
            mosaic[yc:h, xc:w] = img
            
    return mosaic

def create_mixup(img1, img2, alpha=0.4):
    """Create a MixUp augmentation (blending two images)"""
    h, w = img1.shape[:2]
    img2_res = cv2.resize(img2, (w, h))
    
    mixed = cv2.addWeighted(img1, 1 - alpha, img2_res, alpha, 0)
    return mixed

def main():
    # Source images path (adjust to your project structure)
    dataset_path = Path("/Users/caoduong22102004gmail.com/waste-classification-vn/yolo-dataset-merged/images/train")
    output_dir = Path("/Users/caoduong22102004gmail.com/waste-classification-vn/docs/images")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get a few sample images
    image_files = list(dataset_path.glob("*.jpg"))
    if not image_files:
        print(f"Error: No images found in {dataset_path}")
        return
        
    random.shuffle(image_files)
    samples = [cv2.imread(str(f)) for f in image_files[:4]]
    
    # 1. Original
    original = cv2.cvtColor(samples[0], cv2.COLOR_BGR2RGB)
    
    # 2. Geometric & Color
    geom_color = apply_hsv_jitter(apply_geometric(samples[0]))
    geom_color = cv2.cvtColor(geom_color, cv2.COLOR_BGR2RGB)
    
    # 3. Mosaic
    mosaic = create_mosaic(samples)
    mosaic = cv2.cvtColor(mosaic, cv2.COLOR_BGR2RGB)
    
    # 4. MixUp
    mixup = create_mixup(samples[0], samples[1])
    mixup = cv2.cvtColor(mixup, cv2.COLOR_BGR2RGB)
    
    # Plotting
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    
    axes[0, 0].imshow(original)
    axes[0, 0].set_title("1. Ảnh Gốc (Original)", fontsize=14, fontweight='bold')
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(geom_color)
    axes[0, 1].set_title("2. Biến đổi Hình học & Màu sắc\n(Geometric + HSV Jitter)", fontsize=14, fontweight='bold')
    axes[0, 1].axis('off')
    
    axes[1, 0].imshow(mosaic)
    axes[1, 0].set_title("3. Mosaic (Ghép 4 ảnh)", fontsize=14, fontweight='bold')
    axes[1, 0].axis('off')
    
    axes[1, 1].imshow(mixup)
    axes[1, 1].set_title("4. MixUp (Trộn 2 ảnh)", fontsize=14, fontweight='bold')
    axes[1, 1].axis('off')
    
    plt.tight_layout()
    save_path = output_dir / "augmentation_samples.png"
    plt.savefig(save_path, dpi=300)
    print(f"Visualization saved to: {save_path}")

if __name__ == "__main__":
    main()
