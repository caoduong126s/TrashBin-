#!/usr/bin/env python3
"""
Dataset Quality Analysis Script
Analyzes data before and after cleaning process
"""

import os
from pathlib import Path
from collections import defaultdict
import json

def analyze_original_dataset(base_path):
    """Analyze yolo-dataset (original data)"""
    print("=" * 80)
    print("ORIGINAL DATASET ANALYSIS (yolo-dataset)")
    print("=" * 80)
    
    train_path = base_path / "yolo-dataset" / "train"
    
    if not train_path.exists():
        print(f" Path not found: {train_path}")
        return {}
    
    stats = {}
    total_images = 0
    total_labels = 0
    
    # Analyze each class folder
    for class_folder in sorted(train_path.iterdir()):
        if not class_folder.is_dir() or class_folder.name.startswith('.'):
            continue
            
        class_name = class_folder.name
        images = list(class_folder.glob("*.jpg")) + list(class_folder.glob("*.png"))
        labels = list(class_folder.glob("*.txt"))
        
        stats[class_name] = {
            'images': len(images),
            'labels': len(labels),
            'path': str(class_folder)
        }
        
        total_images += len(images)
        total_labels += len(labels)
        
        print(f"\n {class_name}:")
        print(f"   Images: {len(images)}")
        print(f"   Labels: {len(labels)}")
        print(f"   Match: {'YES' if len(images) == len(labels) else 'NO'}")
    
    print(f"\n{'' * 80}")
    print(f"TOTAL - Images: {total_images} | Labels: {total_labels}")
    print(f"Overall Match: {'YES' if total_images == total_labels else 'NO'}")
    
    return stats

def analyze_roboflow_exports(base_path):
    """Analyze roboflow-exports (cleaned data by class)"""
    print("\n" + "=" * 80)
    print("ROBOFLOW EXPORTS ANALYSIS (roboflow-exports)")
    print("=" * 80)
    
    roboflow_path = base_path / "roboflow-exports"
    
    if not roboflow_path.exists():
        print(f" Path not found: {roboflow_path}")
        return {}
    
    stats = {}
    total_files = 0
    
    # Analyze each class folder
    for class_folder in sorted(roboflow_path.iterdir()):
        if not class_folder.is_dir() or class_folder.name.startswith('.'):
            continue
            
        class_name = class_folder.name
        
        # Count all files
        all_files = list(class_folder.rglob("*"))
        files = [f for f in all_files if f.is_file() and not f.name.startswith('.')]
        
        # Separate by type
        images = [f for f in files if f.suffix.lower() in ['.jpg', '.png', '.jpeg']]
        labels = [f for f in files if f.suffix == '.txt' and 'README' not in f.name]
        other = [f for f in files if f not in images and f not in labels]
        
        stats[class_name] = {
            'total_files': len(files),
            'images': len(images),
            'labels': len(labels),
            'other': len(other),
            'path': str(class_folder)
        }
        
        total_files += len(files)
        
        print(f"\n {class_name}:")
        print(f"   Total files: {len(files)}")
        print(f"   Images: {len(images)}")
        print(f"   Labels: {len(labels)}")
        print(f"   Other: {len(other)}")
        
        if len(other) > 0:
            print(f"   Other file types: {set(f.suffix for f in other)}")
    
    print(f"\n{'' * 80}")
    print(f"TOTAL FILES: {total_files}")
    
    return stats

def analyze_merged_dataset(base_path):
    """Analyze yolo-dataset-merged (final merged dataset)"""
    print("\n" + "=" * 80)
    print("MERGED DATASET ANALYSIS (yolo-dataset-merged)")
    print("=" * 80)
    
    merged_path = base_path / "yolo-dataset-merged"
    
    if not merged_path.exists():
        print(f" Path not found: {merged_path}")
        return {}
    
    stats = {
        'train': {'images': 0, 'labels': 0},
        'val': {'images': 0, 'labels': 0}
    }
    
    # Analyze train and val splits
    for split in ['train', 'val']:
        img_path = merged_path / "images" / split
        lbl_path = merged_path / "labels" / split
        
        if img_path.exists():
            images = list(img_path.glob("*.jpg")) + list(img_path.glob("*.png"))
            stats[split]['images'] = len(images)
        
        if lbl_path.exists():
            labels = list(lbl_path.glob("*.txt"))
            stats[split]['labels'] = len(labels)
        
        print(f"\n {split.upper()} Split:")
        print(f"   Images: {stats[split]['images']}")
        print(f"   Labels: {stats[split]['labels']}")
        print(f"   Match: {'YES' if stats[split]['images'] == stats[split]['labels'] else ' NO'}")
    
    total_images = stats['train']['images'] + stats['val']['images']
    total_labels = stats['train']['labels'] + stats['val']['labels']
    
    print(f"\n{'' * 80}")
    print(f"TOTAL - Images: {total_images} | Labels: {total_labels}")
    print(f"Overall Match: {'YES' if total_images == total_labels else ' NO'}")
    
    # Check data.yaml
    yaml_path = merged_path / "data.yaml"
    if yaml_path.exists():
        print(f"\n data.yaml exists")
        with open(yaml_path, 'r', encoding='utf-8') as f:
            print(f"\ndata.yaml content:")
            print(f.read())
    else:
        print(f"\n data.yaml NOT FOUND")
    
    return stats

def analyze_label_content(base_path):
    """Analyze label file content for class distribution"""
    print("\n" + "=" * 80)
    print("LABEL CONTENT ANALYSIS (Class Distribution)")
    print("=" * 80)
    
    merged_path = base_path / "yolo-dataset-merged"
    class_counts = defaultdict(int)
    
    for split in ['train', 'val']:
        lbl_path = merged_path / "labels" / split
        if not lbl_path.exists():
            continue
            
        for label_file in lbl_path.glob("*.txt"):
            try:
                with open(label_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            class_id = int(line.split()[0])
                            class_counts[class_id] += 1
            except Exception as e:
                print(f"  Error reading {label_file.name}: {e}")
    
    # Class names from data.yaml
    class_names = {
        0: 'Nhua',
        1: 'Pin',
        2: 'Vai',
        3: 'Kim loai',
        4: 'Rac thai',
        5: 'Thuy tinh',
        6: 'Giay',
        7: 'Hop giay',
        8: 'Huu co'
    }
    
    print("\n Object Count by Class:")
    total_objects = 0
    for class_id in sorted(class_counts.keys()):
        count = class_counts[class_id]
        total_objects += count
        class_name = class_names.get(class_id, f"Unknown_{class_id}")
        print(f"   Class {class_id} ({class_name}): {count} objects")
    
    print(f"\n{'' * 80}")
    print(f"TOTAL OBJECTS: {total_objects}")
    
    return class_counts

def generate_summary_report(original, roboflow, merged, class_dist):
    """Generate comprehensive summary report"""
    print("\n" + "=" * 80)
    print("SUMMARY REPORT")
    print("=" * 80)
    
    print("\n DATA FLOW:")
    print("   1. Original Dataset (yolo-dataset)")
    print("   2. ↓ Cleaned & Organized by Class (roboflow-exports)")
    print("   3. ↓ Merged & Split (yolo-dataset-merged)")
    print("   4. ↓ Training (train_optimized.py)")
    
    print("\n DATA STATISTICS:")
    
    # Original dataset total
    if original:
        orig_total = sum(s['images'] for s in original.values())
        print(f"   Original Dataset: {orig_total} images across {len(original)} classes")
    
    # Roboflow exports total
    if roboflow:
        robo_total = sum(s['images'] for s in roboflow.values())
        print(f"   Roboflow Exports: {robo_total} images across {len(roboflow)} classes")
    
    # Merged dataset total
    if merged:
        merged_total = merged['train']['images'] + merged['val']['images']
        train_pct = (merged['train']['images'] / merged_total * 100) if merged_total > 0 else 0
        val_pct = (merged['val']['images'] / merged_total * 100) if merged_total > 0 else 0
        print(f"   Merged Dataset: {merged_total} images")
        print(f"      - Train: {merged['train']['images']} ({train_pct:.1f}%)")
        print(f"      - Val: {merged['val']['images']} ({val_pct:.1f}%)")
    
    # Class distribution
    if class_dist:
        total_objs = sum(class_dist.values())
        print(f"   Total Objects Annotated: {total_objs}")
        avg_per_class = total_objs / len(class_dist) if class_dist else 0
        print(f"   Average per Class: {avg_per_class:.1f}")
    
    print("\n QUALITY CHECKS:")
    
    # Check 1: Image-Label matching
    if merged:
        train_match = merged['train']['images'] == merged['train']['labels']
        val_match = merged['val']['images'] == merged['val']['labels']
        print(f"    Train images-labels match: {' YES' if train_match else ' NO'}")
        print(f"    Val images-labels match: {' YES' if val_match else ' NO'}")
    
    # Check 2: All classes present
    if class_dist:
        all_classes_present = len(class_dist) == 9
        print(f"    All 9 classes present: {'YES' if all_classes_present else ' NO'}")
    
    # Check 3: Class balance
    if class_dist:
        counts = list(class_dist.values())
        min_count = min(counts)
        max_count = max(counts)
        balance_ratio = min_count / max_count if max_count > 0 else 0
        print(f"    Class balance ratio: {balance_ratio:.2f} (min/max)")
        if balance_ratio < 0.3:
            print(f"        WARNING: Significant class imbalance detected!")
    
    print("\n" + "=" * 80)

def main():
    base_path = Path("/Users/caoduong22102004gmail.com/Desktop/waste-classification-vn")
    
    print("\n DATASET QUALITY ANALYSIS")
    print(f" Base Path: {base_path}\n")
    
    # Run all analyses
    original_stats = analyze_original_dataset(base_path)
    roboflow_stats = analyze_roboflow_exports(base_path)
    merged_stats = analyze_merged_dataset(base_path)
    class_distribution = analyze_label_content(base_path)
    
    # Generate summary
    generate_summary_report(original_stats, roboflow_stats, merged_stats, class_distribution)
    
    print("\n Analysis Complete!\n")

if __name__ == "__main__":
    main()
