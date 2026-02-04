#!/usr/bin/env python3
"""
Dataset Visualization Script
Creates comprehensive charts comparing before/after cleaning and per-class analysis
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
from collections import defaultdict
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def get_original_stats():
    """Get statistics from original dataset"""
    base_path = Path("/Users/caoduong22102004gmail.com/Desktop/waste-classification-vn")
    train_path = base_path / "yolo-dataset" / "train"
    
    stats = {}
    for class_folder in sorted(train_path.iterdir()):
        if not class_folder.is_dir() or class_folder.name.startswith('.'):
            continue
        class_name = class_folder.name
        images = list(class_folder.glob("*.jpg")) + list(class_folder.glob("*.png"))
        stats[class_name] = len(images)
    
    return stats

def get_roboflow_stats():
    """Get statistics from roboflow exports"""
    base_path = Path("/Users/caoduong22102004gmail.com/Desktop/waste-classification-vn")
    roboflow_path = base_path / "roboflow-exports"
    
    stats = {}
    for class_folder in sorted(roboflow_path.iterdir()):
        if not class_folder.is_dir() or class_folder.name.startswith('.'):
            continue
        class_name = class_folder.name
        all_files = list(class_folder.rglob("*"))
        images = [f for f in all_files if f.is_file() and f.suffix.lower() in ['.jpg', '.png', '.jpeg']]
        stats[class_name] = len(images)
    
    return stats

def get_merged_stats():
    """Get statistics from merged dataset"""
    base_path = Path("/Users/caoduong22102004gmail.com/Desktop/waste-classification-vn")
    merged_path = base_path / "yolo-dataset-merged"
    
    # Count images
    train_images = len(list((merged_path / "images" / "train").glob("*.jpg")))
    val_images = len(list((merged_path / "images" / "val").glob("*.jpg")))
    
    # Count objects per class
    class_counts = defaultdict(int)
    class_names = {
        0: 'Nhua', 1: 'Pin', 2: 'Vai', 3: 'Kim_loai',
        4: 'Rac_thai', 5: 'Thuy_tinh', 6: 'Giay',
        7: 'Hop_giay', 8: 'Huu_co'
    }
    
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
            except:
                pass
    
    return {
        'train': train_images,
        'val': val_images,
        'total': train_images + val_images,
        'class_objects': {class_names[k]: v for k, v in class_counts.items()}
    }

def normalize_class_names(stats_dict):
    """Normalize class names for comparison"""
    name_mapping = {
        'Giấy': 'Giay',
        'Hộp giấy': 'Hop_giay',
        'Hữu cơ': 'Huu_co',
        'Kim loại': 'Kim_loai',
        'Nhựa': 'Nhua',
        'Pin': 'Pin',
        'Rác thải': 'Rac_thai',
        'Thủy tinh': 'Thuy_tinh',
        'Vải': 'Vai'
    }
    
    normalized = {}
    for key, value in stats_dict.items():
        normalized_key = name_mapping.get(key, key)
        normalized[normalized_key] = value
    
    return normalized

def create_before_after_comparison():
    """Create before/after cleaning comparison chart"""
    original = normalize_class_names(get_original_stats())
    roboflow = get_roboflow_stats()
    
    # Ensure same order
    classes = sorted(set(original.keys()) | set(roboflow.keys()))
    
    original_counts = [original.get(c, 0) for c in classes]
    roboflow_counts = [roboflow.get(c, 0) for c in classes]
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Chart 1: Side-by-side comparison
    x = np.arange(len(classes))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, original_counts, width, label='Trước làm sạch', 
                    color='#ff6b6b', alpha=0.8)
    bars2 = ax1.bar(x + width/2, roboflow_counts, width, label='Sau làm sạch', 
                    color='#6bcf7f', alpha=0.8)
    
    ax1.set_xlabel('Classes', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Số lượng ảnh', fontsize=12, fontweight='bold')
    ax1.set_title('So sánh số lượng ảnh: Trước vs Sau làm sạch', 
                  fontsize=14, fontweight='bold', pad=20)
    ax1.set_xticks(x)
    ax1.set_xticklabels(classes, rotation=45, ha='right')
    ax1.legend(fontsize=11)
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9)
    
    # Chart 2: Reduction percentage
    reduction_pct = [(original.get(c, 0) - roboflow.get(c, 0)) / original.get(c, 1) * 100 
                     if original.get(c, 0) > 0 else 0 for c in classes]
    
    colors = ['#ff6b6b' if pct > 0 else '#6bcf7f' for pct in reduction_pct]
    bars3 = ax2.barh(classes, reduction_pct, color=colors, alpha=0.8)
    
    ax2.set_xlabel('% Giảm (-) / Tăng (+)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Classes', fontsize=12, fontweight='bold')
    ax2.set_title('Tỷ lệ thay đổi sau làm sạch', 
                  fontsize=14, fontweight='bold', pad=20)
    ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    ax2.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, pct) in enumerate(zip(bars3, reduction_pct)):
        ax2.text(pct + (1 if pct > 0 else -1), i, f'{pct:.1f}%',
                ha='left' if pct > 0 else 'right', va='center', fontsize=9)
    
    plt.tight_layout()
    
    output_path = Path("/Users/caoduong22102004gmail.com/.gemini/antigravity/brain/9e9d72ec-f935-4337-9022-eed4e5b66771/chart_before_after.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f" Saved: {output_path}")
    plt.close()

def create_per_class_analysis():
    """Create detailed per-class analysis"""
    original = normalize_class_names(get_original_stats())
    roboflow = get_roboflow_stats()
    merged = get_merged_stats()
    
    classes = sorted(set(original.keys()) | set(roboflow.keys()))
    
    # Ensure we only have 9 classes (3x3 grid)
    classes = classes[:9]
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 3, figsize=(18, 14))
    axes = axes.flatten()
    
    for idx, class_name in enumerate(classes):
        if idx >= 9:  # Safety check
            break
            
        ax = axes[idx]
        
        orig_count = original.get(class_name, 0)
        robo_count = roboflow.get(class_name, 0)
        obj_count = merged['class_objects'].get(class_name, 0)
        
        # Data for this class
        stages = ['Gốc\n(Unlabeled)', 'Sau làm sạch\n(Labeled)', 'Objects\n(Annotated)']
        counts = [orig_count, robo_count, obj_count]
        colors = ['#ff6b6b', '#ffd93d', '#6bcf7f']
        
        bars = ax.bar(stages, counts, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        # Add value labels
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(count)}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Calculate reduction
        reduction = orig_count - robo_count
        reduction_pct = (reduction / orig_count * 100) if orig_count > 0 else 0
        
        ax.set_title(f'{class_name}\n({reduction_pct:+.1f}% change)', 
                    fontsize=12, fontweight='bold', pad=10)
        ax.set_ylabel('Count', fontsize=10)
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(0, max(counts) * 1.2 if max(counts) > 0 else 10)
    
    plt.suptitle('Phân tích chi tiết từng Class: Gốc → Làm sạch → Annotations', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    output_path = Path("/Users/caoduong22102004gmail.com/.gemini/antigravity/brain/9e9d72ec-f935-4337-9022-eed4e5b66771/chart_per_class.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f" Saved: {output_path}")
    plt.close()


def create_class_distribution():
    """Create class distribution pie charts"""
    original = normalize_class_names(get_original_stats())
    roboflow = get_roboflow_stats()
    merged = get_merged_stats()
    
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 6))
    
    # Original distribution
    classes_orig = list(original.keys())
    counts_orig = list(original.values())
    colors1 = plt.cm.Set3(np.linspace(0, 1, len(classes_orig)))
    
    wedges1, texts1, autotexts1 = ax1.pie(counts_orig, labels=classes_orig, autopct='%1.1f%%',
                                            colors=colors1, startangle=90, textprops={'fontsize': 9})
    ax1.set_title('Dataset Gốc\n(10,125 images)', fontsize=13, fontweight='bold', pad=15)
    
    # Roboflow distribution
    classes_robo = list(roboflow.keys())
    counts_robo = list(roboflow.values())
    colors2 = plt.cm.Set3(np.linspace(0, 1, len(classes_robo)))
    
    wedges2, texts2, autotexts2 = ax2.pie(counts_robo, labels=classes_robo, autopct='%1.1f%%',
                                            colors=colors2, startangle=90, textprops={'fontsize': 9})
    ax2.set_title('Sau làm sạch\n(8,185 images)', fontsize=13, fontweight='bold', pad=15)
    
    # Object distribution
    classes_obj = list(merged['class_objects'].keys())
    counts_obj = list(merged['class_objects'].values())
    colors3 = plt.cm.Set3(np.linspace(0, 1, len(classes_obj)))
    
    wedges3, texts3, autotexts3 = ax3.pie(counts_obj, labels=classes_obj, autopct='%1.1f%%',
                                            colors=colors3, startangle=90, textprops={'fontsize': 9})
    ax3.set_title('Objects Annotated\n(10,657 objects)', fontsize=13, fontweight='bold', pad=15)
    
    plt.suptitle('Phân bố Classes qua các giai đoạn', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    output_path = Path("/Users/caoduong22102004gmail.com/.gemini/antigravity/brain/9e9d72ec-f935-4337-9022-eed4e5b66771/chart_distribution.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f" Saved: {output_path}")
    plt.close()

def create_summary_chart():
    """Create overall summary chart"""
    original = normalize_class_names(get_original_stats())
    merged = get_merged_stats()
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Chart 1: Overall data flow
    stages = ['Dataset Gốc', 'Sau làm sạch', 'Train Split', 'Val Split']
    counts = [sum(original.values()), merged['total'], merged['train'], merged['val']]
    colors = ['#ff6b6b', '#ffd93d', '#6bcf7f', '#4d96ff']
    
    bars = ax1.bar(stages, counts, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
    ax1.set_ylabel('Số lượng ảnh', fontsize=12, fontweight='bold')
    ax1.set_title('Luồng xử lý dữ liệu', fontsize=14, fontweight='bold', pad=15)
    ax1.grid(axis='y', alpha=0.3)
    
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(count)}\n({count/counts[0]*100:.1f}%)',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Chart 2: Train/Val split
    splits = ['Train (80%)', 'Val (20%)']
    split_counts = [merged['train'], merged['val']]
    split_colors = ['#6bcf7f', '#4d96ff']
    
    wedges, texts, autotexts = ax2.pie(split_counts, labels=splits, autopct='%1.1f%%',
                                        colors=split_colors, startangle=90, 
                                        textprops={'fontsize': 12, 'fontweight': 'bold'})
    ax2.set_title('Train/Val Split', fontsize=14, fontweight='bold', pad=15)
    
    # Chart 3: Data quality metrics
    metrics = ['Images\nMatched', 'Labels\nMatched', 'Classes\nPresent', 'Balance\nRatio']
    values = [100, 100, 100, 57]  # All in percentage
    colors_metrics = ['#6bcf7f' if v >= 80 else '#ffd93d' if v >= 50 else '#ff6b6b' for v in values]
    
    bars3 = ax3.barh(metrics, values, color=colors_metrics, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax3.set_xlabel('Score (%)', fontsize=12, fontweight='bold')
    ax3.set_title('Chỉ số chất lượng dữ liệu', fontsize=14, fontweight='bold', pad=15)
    ax3.set_xlim(0, 110)
    ax3.grid(axis='x', alpha=0.3)
    
    for bar, value in zip(bars3, values):
        ax3.text(value + 2, bar.get_y() + bar.get_height()/2.,
                f'{value}%',
                ha='left', va='center', fontsize=11, fontweight='bold')
    
    # Chart 4: Objects per class
    class_names = list(merged['class_objects'].keys())
    obj_counts = list(merged['class_objects'].values())
    
    bars4 = ax4.bar(class_names, obj_counts, color='#6bcf7f', alpha=0.8, edgecolor='black', linewidth=1.5)
    ax4.set_xlabel('Classes', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Số lượng objects', fontsize=12, fontweight='bold')
    ax4.set_title('Phân bố Objects theo Class', fontsize=14, fontweight='bold', pad=15)
    ax4.set_xticklabels(class_names, rotation=45, ha='right')
    ax4.grid(axis='y', alpha=0.3)
    
    # Add average line
    avg_objects = np.mean(obj_counts)
    ax4.axhline(y=avg_objects, color='red', linestyle='--', linewidth=2, label=f'Trung bình: {avg_objects:.0f}')
    ax4.legend(fontsize=10)
    
    for bar in bars4:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=9)
    
    plt.suptitle('Tổng quan Dataset - Trước và Sau làm sạch', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    output_path = Path("/Users/caoduong22102004gmail.com/.gemini/antigravity/brain/9e9d72ec-f935-4337-9022-eed4e5b66771/chart_summary.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f" Saved: {output_path}")
    plt.close()

def main():
    print("\n" + "="*80)
    print("CREATING VISUALIZATION CHARTS")
    print("="*80 + "\n")
    
    print(" Generating charts...\n")
    
    create_before_after_comparison()
    create_per_class_analysis()
    create_class_distribution()
    create_summary_chart()
    
    print("\n" + "="*80)
    print(" All charts created successfully!")
    print("="*80 + "\n")
    
    print(" Charts saved to:")
    print("   - chart_before_after.png")
    print("   - chart_per_class.png")
    print("   - chart_distribution.png")
    print("   - chart_summary.png\n")

if __name__ == "__main__":
    main()
