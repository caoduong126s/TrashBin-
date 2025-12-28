#!/usr/bin/env python3
"""
CLASS MERGING SCRIPT
====================
Merge similar classes to create more balanced dataset:
- Glass types (3 → 1): green-glass, brown-glass, white-glass → glass
- Textile (2 → 1): clothes, shoes → textile

12 classes → 9 classes
"""

import os
import shutil
from pathlib import Path
from tqdm import tqdm
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

# Define merge mapping
MERGE_MAPPING = {
    # Glass family (merge 3 → 1)
    'green-glass': 'glass',
    'brown-glass': 'glass',
    'white-glass': 'glass',
    
    # Textile family (merge 2 → 1)
    'clothes': 'textile',
    'shoes': 'textile',
    
    # Keep as-is
    'battery': 'battery',
    'biological': 'biological',
    'cardboard': 'cardboard',
    'metal': 'metal',
    'paper': 'paper',
    'plastic': 'plastic',
    'trash': 'trash',
}

# Paths
SOURCE_DIR = Path('data/raw')
TARGET_DIR = Path('data/processed')

# Final class list (9 classes)
FINAL_CLASSES = sorted(set(MERGE_MAPPING.values()))

print("="*70)
print("CLASS MERGING: 12 → 9 CLASSES")
print("="*70)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_directory_structure(base_dir, splits=['train', 'val', 'test']):
    """
    Create directory structure for processed dataset
    """
    print(f"\n📁 Creating directory structure at: {base_dir}")
    
    for split in splits:
        for class_name in FINAL_CLASSES:
            class_dir = base_dir / split / class_name
            class_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Created {len(splits)} splits × {len(FINAL_CLASSES)} classes")
    print(f"   Total directories: {len(splits) * len(FINAL_CLASSES)}")


def copy_and_merge_images(source_dir, target_dir, merge_mapping):
    """
    Copy images from source to target, merging classes according to mapping
    """
    print("\n🔄 Copying and merging images...")
    
    stats = {
        'train': {},
        'val': {},
        'test': {}
    }
    
    for split in ['train', 'val', 'test']:
        print(f"\n📂 Processing {split}/ split...")
        
        source_split = source_dir / split
        target_split = target_dir / split
        
        if not source_split.exists():
            print(f"   ⚠️  {split}/ not found, skipping...")
            continue
        
        # Get all original class directories
        original_classes = [d.name for d in source_split.iterdir() if d.is_dir()]
        
        for original_class in tqdm(original_classes, desc=f"  {split}"):
            # Skip hidden directories
            if original_class.startswith('.'):
                continue
            
            # Get target class name
            target_class = merge_mapping.get(original_class, original_class)
            
            # Source and target directories
            source_class_dir = source_split / original_class
            target_class_dir = target_split / target_class
            
            # Find all images
            images = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
                images.extend(list(source_class_dir.glob(ext)))
            
            # Copy images
            for img_path in images:
                # Create new filename to avoid conflicts
                # Format: originalclass_filename.jpg
                new_filename = f"{original_class}_{img_path.name}"
                target_path = target_class_dir / new_filename
                
                # Copy file
                shutil.copy2(img_path, target_path)
            
            # Update statistics
            if target_class not in stats[split]:
                stats[split][target_class] = 0
            stats[split][target_class] += len(images)
    
    return stats


def generate_statistics(stats):
    """
    Generate and display statistics about merged dataset
    """
    print("\n" + "="*70)
    print("📊 MERGED DATASET STATISTICS")
    print("="*70)
    
    # Calculate totals
    total_images = 0
    class_totals = {}
    
    for split, classes in stats.items():
        for class_name, count in classes.items():
            total_images += count
            if class_name not in class_totals:
                class_totals[class_name] = 0
            class_totals[class_name] += count
    
    # Display per-class statistics
    print(f"\n{'Class':<15s} {'Train':>8s} {'Val':>8s} {'Test':>8s} {'Total':>8s}")
    print("-" * 70)
    
    for class_name in sorted(FINAL_CLASSES):
        train_count = stats['train'].get(class_name, 0)
        val_count = stats['val'].get(class_name, 0)
        test_count = stats['test'].get(class_name, 0)
        total = class_totals.get(class_name, 0)
        
        print(f"{class_name:<15s} {train_count:>8d} {val_count:>8d} {test_count:>8d} {total:>8d}")
    
    print("-" * 70)
    
    # Totals
    train_total = sum(stats['train'].values())
    val_total = sum(stats['val'].values())
    test_total = sum(stats['test'].values())
    
    print(f"{'TOTAL':<15s} {train_total:>8d} {val_total:>8d} {test_total:>8d} {total_images:>8d}")
    
    # Percentages
    train_pct = train_total / total_images * 100
    val_pct = val_total / total_images * 100
    test_pct = test_total / total_images * 100
    
    print(f"{'PERCENTAGE':<15s} {train_pct:>7.1f}% {val_pct:>7.1f}% {test_pct:>7.1f}% {100.0:>7.1f}%")
    
    # Class imbalance
    print(f"\n📈 Class Balance:")
    max_class = max(class_totals.items(), key=lambda x: x[1])
    min_class = min(class_totals.items(), key=lambda x: x[1])
    imbalance_ratio = max_class[1] / min_class[1]
    
    print(f"   Largest class: {max_class[0]} ({max_class[1]:,} images)")
    print(f"   Smallest class: {min_class[0]} ({min_class[1]:,} images)")
    print(f"   Imbalance ratio: {imbalance_ratio:.2f}:1")
    
    return stats, class_totals


def save_merge_info(target_dir, merge_mapping, stats, class_totals):
    """
    Save merge information to JSON file
    """
    metadata = {
        'merge_mapping': merge_mapping,
        'original_classes': list(set(merge_mapping.keys())),
        'final_classes': FINAL_CLASSES,
        'num_original_classes': len(set(merge_mapping.keys())),
        'num_final_classes': len(FINAL_CLASSES),
        'statistics': {
            'by_split': stats,
            'by_class': class_totals,
            'total_images': sum(class_totals.values())
        },
        'imbalance': {
            'max_class': max(class_totals.items(), key=lambda x: x[1])[0],
            'max_count': max(class_totals.values()),
            'min_class': min(class_totals.items(), key=lambda x: x[1])[0],
            'min_count': min(class_totals.values()),
            'ratio': max(class_totals.values()) / min(class_totals.values())
        }
    }
    
    output_path = target_dir / 'merge_info.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Merge information saved to: {output_path}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function
    """
    # Check source directory exists
    if not SOURCE_DIR.exists():
        print(f"❌ ERROR: Source directory not found: {SOURCE_DIR}")
        print(f"   Please make sure data/raw/ exists and contains train/val/test splits")
        return
    
    # Create target directory structure
    create_directory_structure(TARGET_DIR)
    
    # Copy and merge images
    stats = copy_and_merge_images(SOURCE_DIR, TARGET_DIR, MERGE_MAPPING)
    
    # Generate statistics
    stats, class_totals = generate_statistics(stats)
    
    # Save metadata
    save_merge_info(TARGET_DIR, MERGE_MAPPING, stats, class_totals)
    
    # Final summary
    print("\n" + "="*70)
    print("✅ CLASS MERGING COMPLETED!")
    print("="*70)
    print(f"\n📁 Source: {SOURCE_DIR.absolute()}")
    print(f"📁 Target: {TARGET_DIR.absolute()}")
    print(f"\n📊 Summary:")
    print(f"   Original classes: {len(set(MERGE_MAPPING.keys()))}")
    print(f"   Final classes: {len(FINAL_CLASSES)}")
    print(f"   Total images: {sum(class_totals.values()):,}")
    print(f"\n🎯 Classes: {', '.join(FINAL_CLASSES)}")
    print("\n✅ Ready for Step 3.2: Class Weights Calculation!")
    print("="*70)


if __name__ == '__main__':
    main()
