#!/usr/bin/env python3
"""
DATA AUGMENTATION PIPELINE
===========================
Setup augmentation strategy with differential augmentation based on class size.
Uses albumentations library for efficient augmentations.
"""

import json
import cv2
import numpy as np
from pathlib import Path
import albumentations as A
from albumentations.pytorch import ToTensorV2
import matplotlib.pyplot as plt
from PIL import Image

# ============================================================================
# CONFIGURATION
# ============================================================================

print("="*70)
print("DATA AUGMENTATION PIPELINE SETUP")
print("="*70)

# Image size for training
IMG_SIZE = 224

# ============================================================================
# AUGMENTATION STRATEGIES
# ============================================================================

def get_light_augmentation():
    """
    Light augmentation for large classes (e.g., textile)
    Apply minimal transformations
    """
    return A.Compose([
        # Geometric
        A.HorizontalFlip(p=0.5),
        A.Rotate(limit=15, p=0.3),
        
        # Color
        A.RandomBrightnessContrast(
            brightness_limit=0.1,
            contrast_limit=0.1,
            p=0.3
        ),
        
        # Resize and normalize
        A.Resize(IMG_SIZE, IMG_SIZE),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2()
    ])


def get_medium_augmentation():
    """
    Medium augmentation for medium-sized classes
    """
    return A.Compose([
        # Geometric
        A.HorizontalFlip(p=0.5),
        A.Rotate(limit=20, p=0.5),
        A.ShiftScaleRotate(
            shift_limit=0.1,
            scale_limit=0.1,
            rotate_limit=20,
            p=0.5
        ),
        
        # Color
        A.RandomBrightnessContrast(
            brightness_limit=0.2,
            contrast_limit=0.2,
            p=0.5
        ),
        A.HueSaturationValue(
            hue_shift_limit=10,
            sat_shift_limit=20,
            val_shift_limit=10,
            p=0.3
        ),
        
        # Quality degradation
        A.GaussianBlur(blur_limit=(3, 5), p=0.2),
        A.ISONoise(p=0.2),
        
        # Resize and normalize
        A.Resize(IMG_SIZE, IMG_SIZE),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2()
    ])


def get_heavy_augmentation():
    """
    Heavy augmentation for small classes (e.g., trash, brown-glass)
    Apply aggressive transformations to increase diversity
    """
    return A.Compose([
        # Geometric
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.2),
        A.Rotate(limit=30, p=0.7),
        A.ShiftScaleRotate(
            shift_limit=0.15,
            scale_limit=0.15,
            rotate_limit=30,
            p=0.7
        ),
        A.Perspective(scale=(0.05, 0.1), p=0.3),
        
        # Color
        A.RandomBrightnessContrast(
            brightness_limit=0.3,
            contrast_limit=0.3,
            p=0.7
        ),
        A.HueSaturationValue(
            hue_shift_limit=20,
            sat_shift_limit=30,
            val_shift_limit=20,
            p=0.5
        ),
        A.RGBShift(
            r_shift_limit=15,
            g_shift_limit=15,
            b_shift_limit=15,
            p=0.5
        ),
        
        # Quality degradation
        A.OneOf([
            A.GaussianBlur(blur_limit=(3, 7), p=1.0),
            A.MotionBlur(blur_limit=5, p=1.0),
        ], p=0.3),
        
        A.OneOf([
            A.ISONoise(p=1.0),
            A.GaussNoise(var_limit=(10, 50), p=1.0),
        ], p=0.3),
        
        A.Downscale(scale_min=0.7, scale_max=0.9, p=0.2),
        
        # Environmental
        A.RandomShadow(p=0.2),
        A.RandomFog(fog_coef_lower=0.1, fog_coef_upper=0.3, p=0.1),
        
        # Resize and normalize
        A.Resize(IMG_SIZE, IMG_SIZE),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2()
    ])


def get_validation_transform():
    """
    No augmentation for validation/test sets
    Only resize and normalize
    """
    return A.Compose([
        A.Resize(IMG_SIZE, IMG_SIZE),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2()
    ])


# ============================================================================
# AUGMENTATION STRATEGY MAPPER
# ============================================================================

def determine_augmentation_strategy(class_counts):
    """
    Determine which augmentation strategy to use for each class
    based on sample count
    
    Strategy:
    - Large classes (> 2000): Light augmentation
    - Medium classes (800-2000): Medium augmentation  
    - Small classes (< 800): Heavy augmentation
    """
    print("\n📊 Determining augmentation strategy per class...")
    
    strategy_map = {}
    
    # Thresholds
    LARGE_THRESHOLD = 2000
    MEDIUM_THRESHOLD = 800
    
    print(f"\n{'Class':<15s} {'Samples':>10s} {'Strategy':>15s}")
    print("-" * 70)
    
    for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
        if count > LARGE_THRESHOLD:
            strategy = 'light'
        elif count > MEDIUM_THRESHOLD:
            strategy = 'medium'
        else:
            strategy = 'heavy'
        
        strategy_map[class_name] = strategy
        print(f"{class_name:<15s} {count:>10,} {strategy:>15s}")
    
    return strategy_map


# ============================================================================
# VISUALIZATION
# ============================================================================

def visualize_augmentations(image_path, output_dir):
    """
    Visualize different augmentation strategies on a sample image
    """
    print(f"\n🎨 Creating augmentation visualizations...")
    
    # Read image
    image = cv2.imread(str(image_path))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Get transforms (without normalization for visualization)
    light_aug = A.Compose([
        A.HorizontalFlip(p=1.0),
        A.Rotate(limit=15, p=1.0),
        A.RandomBrightnessContrast(brightness_limit=0.1, contrast_limit=0.1, p=1.0),
        A.Resize(IMG_SIZE, IMG_SIZE)
    ])
    
    medium_aug = A.Compose([
        A.HorizontalFlip(p=1.0),
        A.Rotate(limit=20, p=1.0),
        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=1.0),
        A.HueSaturationValue(hue_shift_limit=10, sat_shift_limit=20, val_shift_limit=10, p=1.0),
        A.GaussianBlur(blur_limit=(3, 5), p=1.0),
        A.Resize(IMG_SIZE, IMG_SIZE)
    ])
    
    heavy_aug = A.Compose([
        A.HorizontalFlip(p=1.0),
        A.Rotate(limit=30, p=1.0),
        A.ShiftScaleRotate(shift_limit=0.15, scale_limit=0.15, rotate_limit=30, p=1.0),
        A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=1.0),
        A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20, p=1.0),
        A.GaussianBlur(blur_limit=(3, 7), p=1.0),
        A.Resize(IMG_SIZE, IMG_SIZE)
    ])
    
    # Create figure
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    
    # Original
    axes[0, 0].imshow(cv2.resize(image, (IMG_SIZE, IMG_SIZE)))
    axes[0, 0].set_title('Original', fontsize=12, fontweight='bold')
    axes[0, 0].axis('off')
    
    # Light augmentation examples
    for i in range(3):
        aug = light_aug(image=image)['image']
        axes[0, i+1].imshow(aug)
        axes[0, i+1].set_title(f'Light Aug {i+1}', fontsize=12)
        axes[0, i+1].axis('off')
    
    # Medium augmentation
    aug = medium_aug(image=image)['image']
    axes[1, 0].imshow(aug)
    axes[1, 0].set_title('Medium Aug 1', fontsize=12, fontweight='bold')
    axes[1, 0].axis('off')
    
    # Heavy augmentation examples
    for i in range(3):
        aug = heavy_aug(image=image)['image']
        axes[1, i+1].imshow(aug)
        axes[1, i+1].set_title(f'Heavy Aug {i+1}', fontsize=12, fontweight='bold')
        axes[1, i+1].axis('off')
    
    plt.suptitle('Augmentation Strategies Comparison', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Save
    output_path = output_dir / 'augmentation_visualization.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f" Visualization saved to: {output_path}")


# ============================================================================
# SAVE CONFIGURATION
# ============================================================================

def save_augmentation_config(strategy_map, output_dir):
    """
    Save augmentation configuration to JSON
    """
    config = {
        'image_size': IMG_SIZE,
        'normalization': {
            'mean': [0.485, 0.456, 0.406],
            'std': [0.229, 0.224, 0.225]
        },
        'class_strategies': strategy_map,
        'strategies': {
            'light': {
                'description': 'Light augmentation for large classes (>2000 samples)',
                'transformations': [
                    'HorizontalFlip (p=0.5)',
                    'Rotate (±15°, p=0.3)',
                    'RandomBrightnessContrast (±10%, p=0.3)'
                ]
            },
            'medium': {
                'description': 'Medium augmentation for medium classes (800-2000 samples)',
                'transformations': [
                    'HorizontalFlip (p=0.5)',
                    'Rotate (±20°, p=0.5)',
                    'ShiftScaleRotate (p=0.5)',
                    'RandomBrightnessContrast (±20%, p=0.5)',
                    'HueSaturationValue (p=0.3)',
                    'GaussianBlur (p=0.2)',
                    'ISONoise (p=0.2)'
                ]
            },
            'heavy': {
                'description': 'Heavy augmentation for small classes (<800 samples)',
                'transformations': [
                    'HorizontalFlip (p=0.5)',
                    'VerticalFlip (p=0.2)',
                    'Rotate (±30°, p=0.7)',
                    'ShiftScaleRotate (p=0.7)',
                    'Perspective (p=0.3)',
                    'RandomBrightnessContrast (±30%, p=0.7)',
                    'HueSaturationValue (p=0.5)',
                    'RGBShift (p=0.5)',
                    'Blur variants (p=0.3)',
                    'Noise variants (p=0.3)',
                    'Downscale (p=0.2)',
                    'RandomShadow (p=0.2)',
                    'RandomFog (p=0.1)'
                ]
            }
        },
        'usage': {
            'training': 'Apply augmentation based on class strategy',
            'validation': 'No augmentation, only resize and normalize',
            'testing': 'No augmentation, only resize and normalize'
        }
    }
    
    output_path = output_dir / 'augmentation_config.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n Augmentation config saved to: {output_path}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function
    """
    # Paths
    data_dir = Path('data/processed')
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)
    
    # Check if merge info exists
    merge_info_path = data_dir / 'merge_info.json'
    if not merge_info_path.exists():
        print(f" ERROR: merge_info.json not found")
        print(f"   Please run merge_classes.py first!")
        return
    
    # Load class counts
    with open(merge_info_path, 'r') as f:
        merge_info = json.load(f)
    
    class_counts = merge_info['statistics']['by_class']
    
    print(f"\n Loaded class counts for {len(class_counts)} classes")
    
    # Determine augmentation strategy
    strategy_map = determine_augmentation_strategy(class_counts)
    
    # Count strategies
    strategy_counts = {}
    for strategy in strategy_map.values():
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
    
    print(f"\n Strategy distribution:")
    print(f"   Light: {strategy_counts.get('light', 0)} classes")
    print(f"   Medium: {strategy_counts.get('medium', 0)} classes")
    print(f"   Heavy: {strategy_counts.get('heavy', 0)} classes")
    
    # Save configuration
    save_augmentation_config(strategy_map, data_dir)
    
    # Create visualization (if sample image exists)
    print(f"\n🎨 Creating visualization...")
    train_dir = data_dir / 'train'
    
    # Find first image for visualization
    sample_image = None
    for class_dir in train_dir.iterdir():
        if class_dir.is_dir() and not class_dir.name.startswith('.'):
            images = list(class_dir.glob('*.jpg')) + list(class_dir.glob('*.png'))
            if images:
                sample_image = images[0]
                break
    
    if sample_image:
        visualize_augmentations(sample_image, output_dir)
    else:
        print("  No sample image found for visualization")
    
    # Summary
    print("\n" + "="*70)
    print(" AUGMENTATION PIPELINE SETUP COMPLETED!")
    print("="*70)
    print(f"\n Configuration:")
    print(f"   Image size: {IMG_SIZE}×{IMG_SIZE}")
    print(f"   Classes: {len(class_counts)}")
    print(f"   Strategies: {len(set(strategy_map.values()))}")
    print(f"\n Strategy mapping:")
    for strategy in ['light', 'medium', 'heavy']:
        classes = [c for c, s in strategy_map.items() if s == strategy]
        if classes:
            print(f"   {strategy.capitalize():8s}: {', '.join(sorted(classes))}")
    print(f"\n Next steps:")
    print(f"   1. Use augmentation config in data generators")
    print(f"   2. Load config from: augmentation_config.json")
    print(f"   3. Apply transforms during training")
    print("\n Ready for Step 3.4: Data Generators!")
    print("="*70)


if __name__ == '__main__':
    main()
