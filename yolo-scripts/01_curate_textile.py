"""
Curate Textile Dataset
Works with data/processed/train/textile (English names)
Reduce from 4,400+ to 630 most diverse images using clustering
"""

import cv2
import numpy as np
from pathlib import Path
from sklearn.cluster import MiniBatchKMeans
from tqdm import tqdm
import shutil

# Class name mapping (English → Vietnamese)
CLASS_MAPPING = {
    'plastic': 'Nhựa',
    'paper': 'Giấy',
    'cardboard': 'Hộp giấy',
    'metal': 'Kim loại',
    'glass': 'Thủy tinh',
    'battery': 'Pin',
    'biological': 'Hữu cơ',
    'textile': 'Vải',
    'trash': 'Rác thải'
}

def extract_features(image_path, target_size=(64, 64)):
    """Extract simple features for clustering"""
    try:
        img = cv2.imread(str(image_path))
        if img is None:
            return None
        
        img = cv2.resize(img, target_size)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        
        features = np.concatenate([
            img.flatten(),
            hsv.flatten(),
            lab.flatten()
        ])
        
        return features
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def curate_textile(input_dir, output_dir, backup_dir, target_count=630):
    """Curate textile dataset using cluster-based sampling"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    backup_path = Path(backup_dir)
    
    output_path.mkdir(parents=True, exist_ok=True)
    backup_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("TEXTILE CURATION - Cluster-based Sampling")
    print("=" * 60)
    
    # Get all images
    image_files = list(input_path.glob('*.jpg')) + \
                  list(input_path.glob('*.png')) + \
                  list(input_path.glob('*.jpeg'))
    total_images = len(image_files)
    
    print(f"\n Dataset Info:")
    print(f"   Input: {input_path}")
    print(f"   Total images: {total_images}")
    print(f"   Target: {target_count}")
    print(f"   To remove: {total_images - target_count}")
    
    if total_images == 0:
        print(f"\n ERROR: No images found!")
        print(f"   Checked: {input_path}")
        return
    
    if total_images <= target_count:
        print(f"\n Already at or below target! Copying all...")
        for img_path in image_files:
            shutil.copy2(img_path, output_path / img_path.name)
        print(f" Copied {len(image_files)} images")
        return
    
    # Extract features
    print(f"\n Extracting features from {total_images} images...")
    features = []
    valid_images = []
    
    for img_path in tqdm(image_files, desc="Extracting features"):
        feat = extract_features(img_path)
        if feat is not None:
            features.append(feat)
            valid_images.append(img_path)
    
    features = np.array(features)
    print(f" Extracted features: {features.shape}")
    
    print(f"\n Normalizing features...")
    features = (features - features.mean(axis=0)) / (features.std(axis=0) + 1e-8)
    
    print(f"\n Clustering into {target_count} groups...")
    kmeans = MiniBatchKMeans(
        n_clusters=target_count,
        random_state=42,
        batch_size=1000,
        max_iter=100,
        verbose=1
    )
    labels = kmeans.fit_predict(features)
    
    print(f"\n Selecting most representative images...")
    selected_images = []
    
    for cluster_id in tqdm(range(target_count), desc="Selecting from clusters"):
        cluster_mask = labels == cluster_id
        cluster_indices = np.where(cluster_mask)[0]
        
        if len(cluster_indices) == 0:
            continue
        
        cluster_features = features[cluster_mask]
        centroid = kmeans.cluster_centers_[cluster_id]
        distances = np.linalg.norm(cluster_features - centroid, axis=1)
        closest_idx = cluster_indices[np.argmin(distances)]
        
        selected_images.append(valid_images[closest_idx])
    
    print(f"\n Selected {len(selected_images)} diverse images")
    
    print(f"\n Copying selected images...")
    for img_path in tqdm(selected_images, desc="Copying"):
        shutil.copy2(img_path, output_path / img_path.name)
    
    print(f"\n Backing up remaining images...")
    for img_path in tqdm(valid_images, desc="Backing up"):
        if img_path not in selected_images:
            shutil.copy2(img_path, backup_path / img_path.name)
    
    print(f"\n" + "=" * 60)
    print(f" CURATION COMPLETE!")
    print(f"=" * 60)
    print(f" Results:")
    print(f"   Curated: {len(selected_images)} images → {output_path}")
    print(f"   Backed up: {total_images - len(selected_images)} images → {backup_path}")
    print("=" * 60)

if __name__ == "__main__":
    from pathlib import Path
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Dataset is in data/processed/train/ with English names
    INPUT_DIR = project_root / "data/processed/train/textile"
    OUTPUT_DIR = project_root / "yolo-dataset/train/Vải"  # Vietnamese name for output
    BACKUP_DIR = project_root / "yolo-dataset/backup/Vải"
    
    print(f"\n Paths:")
    print(f"   Input:  {INPUT_DIR}")
    print(f"   Output: {OUTPUT_DIR}")
    print(f"   Backup: {BACKUP_DIR}")
    
    if not INPUT_DIR.exists():
        print(f"\n ERROR: Input directory not found!")
        print(f"   Looking for: {INPUT_DIR}")
        print(f"\n Check with: ls -la {INPUT_DIR.parent}")
        exit(1)
    
    curate_textile(
        input_dir=str(INPUT_DIR),
        output_dir=str(OUTPUT_DIR),
        backup_dir=str(BACKUP_DIR),
        target_count=630
    )
    
    print("\n Next steps:")
    print("1. Review curated images in:", OUTPUT_DIR)
    print("2. Run: python 02_curate_glass.py")
