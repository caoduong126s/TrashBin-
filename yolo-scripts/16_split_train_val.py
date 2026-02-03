"""
Split Train Set into Train/Val (80/20)
For YOLO dataset that only has train set
"""

import shutil
from pathlib import Path
import random

def split_train_val(dataset_dir, train_ratio=0.8, seed=42):
    """
    Split train set into train/val
    
    Args:
        dataset_dir: Path to dataset (e.g., yolo-dataset-merged)
        train_ratio: Ratio for training (0.8 = 80% train, 20% val)
        seed: Random seed for reproducibility
    """
    
    print("=" * 60)
    print("SPLIT TRAIN/VAL")
    print("=" * 60)
    
    dataset_path = Path(dataset_dir)
    
    train_images = dataset_path / 'images' / 'train'
    train_labels = dataset_path / 'labels' / 'train'
    val_images = dataset_path / 'images' / 'val'
    val_labels = dataset_path / 'labels' / 'val'
    
    # Get all training images
    image_files = list(train_images.glob('*.jpg')) + list(train_images.glob('*.png'))
    
    if not image_files:
        print(" No images found in train set!")
        return
    
    print(f"\n Total images: {len(image_files)}")
    
    # Shuffle
    random.seed(seed)
    random.shuffle(image_files)
    
    # Split
    split_idx = int(len(image_files) * train_ratio)
    
    train_files = image_files[:split_idx]
    val_files = image_files[split_idx:]
    
    print(f"\n Split:")
    print(f"   Train: {len(train_files)} images ({train_ratio*100:.0f}%)")
    print(f"   Val:   {len(val_files)} images ({(1-train_ratio)*100:.0f}%)")
    
    # Confirm
    response = input(f"\n Proceed with split? (yes/no): ").lower()
    if response not in ['yes', 'y']:
        print("Split cancelled.")
        return
    
    # Create val directories (should already exist but make sure)
    val_images.mkdir(parents=True, exist_ok=True)
    val_labels.mkdir(parents=True, exist_ok=True)
    
    # Move validation files
    print(f"\n Moving validation files...")
    
    moved_images = 0
    moved_labels = 0
    
    for img_file in val_files:
        # Move image
        dest_img = val_images / img_file.name
        shutil.move(str(img_file), str(dest_img))
        moved_images += 1
        
        # Move corresponding label
        label_file = train_labels / img_file.with_suffix('.txt').name
        
        if label_file.exists():
            dest_label = val_labels / label_file.name
            shutil.move(str(label_file), str(dest_label))
            moved_labels += 1
    
    print(f"    Moved {moved_images} images")
    print(f"    Moved {moved_labels} labels")
    
    # Verify
    print(f"\n Verification:")
    
    final_train_images = len(list(train_images.glob('*.*')))
    final_train_labels = len(list(train_labels.glob('*.txt')))
    final_val_images = len(list(val_images.glob('*.*')))
    final_val_labels = len(list(val_labels.glob('*.txt')))
    
    print(f"   Train: {final_train_images} images, {final_train_labels} labels")
    print(f"   Val:   {final_val_images} images, {final_val_labels} labels")
    
    # Check balance
    if final_train_images == final_train_labels and final_val_images == final_val_labels:
        print(f"\n Split successful!")
    else:
        print(f"\n  Warning: Image/label count mismatch")
    
    print("\n" + "=" * 60)
    print(" COMPLETE!")
    print("=" * 60)
    
    print(f"\n Next step:")
    print(f"   python yolo-scripts/15_train_model.py")

if __name__ == "__main__":
    import sys
    
    DATASET_DIR = Path.home() / "waste-classification-vn" / "yolo-dataset-merged"
    
    print("\n" + "=" * 60)
    print("TRAIN/VAL SPLIT")
    print("Vietnamese Waste Detection Dataset")
    print("=" * 60)
    
    print(f"\n Dataset: {DATASET_DIR}")
    
    if not DATASET_DIR.exists():
        print(f" Dataset not found!")
        sys.exit(1)
    
    split_train_val(
        dataset_dir=DATASET_DIR,
        train_ratio=0.8,
        seed=42
    )
