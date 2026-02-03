import os
import yaml
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import cv2
import numpy as np
from tqdm import tqdm
import json

# Set aesthetic style
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'

def analyze_classification_dataset(dataset_path):
    """Analyze a dataset in classification format (folder per class)"""
    print(f"--- Analyzing Classification Dataset: {dataset_path} ---")
    data = []
    
    # Iterate through class folders
    for class_folder in dataset_path.iterdir():
        if class_folder.is_dir():
            class_name = class_folder.name
            images = list(class_folder.glob("*.j*pg")) + list(class_folder.glob("*.png")) + list(class_folder.glob("*.webp"))
            
            for img_path in images:
                # Basic image stats without opening for speed first, 
                # but we need size for EDA
                data.append({
                    "class": class_name,
                    "path": str(img_path),
                    "filename": img_path.name
                })
    
    df = pd.DataFrame(data)
    if df.empty:
        print("No data found in classification dataset.")
        return None
    
    print(f"Total images found: {len(df)}")
    print(df['class'].value_counts())
    return df

def analyze_yolo_dataset(dataset_path):
    """Analyze a dataset in YOLO format"""
    print(f"\n--- Analyzing YOLO Dataset: {dataset_path} ---")
    
    data_yaml = dataset_path / "data.yaml"
    if not data_yaml.exists():
        print(f"Error: data.yaml not found at {data_yaml}")
        return None, None
        
    with open(data_yaml, 'r') as f:
        metadata = yaml.safe_load(f)
        
    class_names = metadata.get('names', [])
    print(f"Classes: {class_names}")
    
    bboxes = []
    image_stats = []
    
    # Analyze train and val splits
    for split in ['train', 'val']:
        img_dir = dataset_path / "images" / split
        lbl_dir = dataset_path / "labels" / split
        
        if not img_dir.exists() or not lbl_dir.exists():
            print(f"Warning: {split} split directories missing.")
            continue
            
        images = list(img_dir.glob("*.j*pg")) + list(img_dir.glob("*.png"))
        print(f"Analyzing {split} split ({len(images)} images)...")
        
        for img_path in tqdm(images, desc=f"Processing {split}"):
            # Read image metadata
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            h, w = img.shape[:2]
            image_stats.append({
                "split": split,
                "width": w,
                "height": h,
                "aspect_ratio": w / h
            })
            
            # Read corresponding label
            lbl_path = lbl_dir / f"{img_path.stem}.txt"
            if lbl_path.exists():
                with open(lbl_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) == 5:
                            cls_id = int(parts[0])
                            x_center = float(parts[1])
                            y_center = float(parts[2])
                            width = float(parts[3])
                            height = float(parts[4])
                            
                            bboxes.append({
                                "split": split,
                                "class_id": cls_id,
                                "class_name": class_names[cls_id] if cls_id < len(class_names) else f"Unknown({cls_id})",
                                "x_center": x_center,
                                "y_center": y_center,
                                "width": width,
                                "height": height,
                                "area": width * height
                            })
    
    df_bboxes = pd.DataFrame(bboxes)
    df_images = pd.DataFrame(image_stats)
    
    return df_bboxes, df_images, class_names

def generate_visualizations(df_class, df_yolo_bbox, df_yolo_img, output_dir):
    """Generate and save EDA plots"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Class Distribution Comparison
    plt.figure(figsize=(12, 6))
    if df_class is not None:
        plt.subplot(1, 2, 1)
        sns.countplot(data=df_class, y='class', order=df_class['class'].value_counts().index, palette="viridis")
        plt.title("Raw Classification Dataset Distribution")
        plt.xlabel("Count")
        
    if df_yolo_bbox is not None:
        plt.subplot(1, 2, 2)
        sns.countplot(data=df_yolo_bbox, y='class_name', order=df_yolo_bbox['class_name'].value_counts().index, palette="magma")
        plt.title("YOLO Bounding Box Class Distribution")
        plt.xlabel("Count")
        
    plt.tight_layout()
    plt.savefig(output_dir / "class_distribution.png", dpi=300)
    plt.close()
    
    # 2. Bounding Box Sizes (Relative to Image)
    if df_yolo_bbox is not None:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df_yolo_bbox, x='width', y='height', hue='class_name', alpha=0.3, s=10)
        plt.title("Bounding Box Dimensions (Normalized)")
        plt.xlabel("Width")
        plt.ylabel("Height")
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.savefig(output_dir / "bbox_dimensions.png", dpi=300)
        plt.close()
        
        # 3. Object Location Heatmap (Centroids)
        plt.figure(figsize=(8, 8))
        sns.kdeplot(data=df_yolo_bbox, x='x_center', y='y_center', fill=True, cmap="rocket", thresh=0.05, levels=100)
        plt.title("Object Centroid Distribution (Heatmap)")
        plt.xlim(0, 1)
        plt.ylim(1, 0) # Flip Y axis for image coords
        plt.savefig(output_dir / "bbox_heatmap.png", dpi=300)
        plt.close()

    # 4. Image Aspect Ratios
    if df_yolo_img is not None:
        plt.figure(figsize=(10, 5))
        sns.histplot(df_yolo_img['aspect_ratio'], bins=30, kde=True, color='teal')
        plt.title("Image Aspect Ratio Distribution")
        plt.xlabel("Width / Height")
        plt.savefig(output_dir / "image_aspect_ratios.png", dpi=300)
        plt.close()

def main():
    root_dir = Path("/Users/caoduong22102004gmail.com/waste-classification-vn")
    class_dataset_path = root_dir / "yolo-dataset" / "train"
    yolo_dataset_path = root_dir / "yolo-dataset-merged"
    output_dir = root_dir / "outputs" / "eda"
    
    # Analyze
    df_class = analyze_classification_dataset(class_dataset_path)
    df_yolo_bbox, df_yolo_img, class_names = analyze_yolo_dataset(yolo_dataset_path)
    
    # Visualize
    generate_visualizations(df_class, df_yolo_bbox, df_yolo_img, output_dir)
    
    # Save statistics summarize
    stats = {
        "classification_dataset": {
            "total_images": len(df_class) if df_class is not None else 0,
            "classes": df_class['class'].value_counts().to_dict() if df_class is not None else {}
        },
        "yolo_dataset": {
            "total_bboxes": len(df_yolo_bbox) if df_yolo_bbox is not None else 0,
            "total_images": len(df_yolo_img) if df_yolo_img is not None else 0,
            "class_distribution": df_yolo_bbox['class_name'].value_counts().to_dict() if df_yolo_bbox is not None else {},
            "avg_img_width": float(df_yolo_img['width'].mean()) if df_yolo_img is not None else 0,
            "avg_img_height": float(df_yolo_img['height'].mean()) if df_yolo_img is not None else 0,
            "avg_bbox_area": float(df_yolo_bbox['area'].mean()) if df_yolo_bbox is not None else 0
        }
    }
    
    with open(output_dir / "summary_stats.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)
        
    print(f"\nEDA Complete! Results saved to {output_dir}")

if __name__ == "__main__":
    main()
