"""
Verify Dataset Distribution
Check image counts and balance ratio
"""

from pathlib import Path

def verify_distribution(dataset_path):
    """Verify final dataset distribution"""
    
    dataset = Path(dataset_path)
    
    print("=" * 60)
    print("DATASET DISTRIBUTION VERIFICATION")
    print("=" * 60)
    print(f"\nChecking: {dataset}")
    
    if not dataset.exists():
        print(f"\n ERROR: Directory not found!")
        print(f"   Path: {dataset}")
        return None, None
    
    counts = {}
    
    for class_dir in sorted(dataset.iterdir()):
        if not class_dir.is_dir():
            continue
        
        # Count all image types
        images = list(class_dir.glob('*.jpg')) + \
                 list(class_dir.glob('*.jpeg')) + \
                 list(class_dir.glob('*.png')) + \
                 list(class_dir.glob('*.JPG')) + \
                 list(class_dir.glob('*.PNG'))
        count = len(images)
        counts[class_dir.name] = count
    
    if not counts:
        print("\n No classes found!")
        print("   Please check if folders exist in:", dataset)
        return None, None
    
    # Display results
    print(f"\n Class Distribution:")
    print("=" * 60)
    
    total = sum(counts.values())
    min_count = min(counts.values())
    max_count = max(counts.values())
    ratio = max_count / min_count if min_count > 0 else 0
    
    for class_name in sorted(counts.keys()):
        count = counts[class_name]
        percentage = (count / total * 100) if total > 0 else 0
        bar_length = int(count / 20)
        bar = "" * bar_length
        
        print(f"{class_name:12s}: {count:5d} ({percentage:5.2f}%) {bar}")
    
    print("=" * 60)
    print(f"\n Statistics:")
    print(f"   Total images: {total:,}")
    print(f"   Classes: {len(counts)}")
    print(f"   Min count: {min_count}")
    print(f"   Max count: {max_count}")
    print(f"   Imbalance ratio: {ratio:.2f}x")
    
    # Evaluation
    print(f"\n Evaluation:")
    if ratio < 1.2:
        print(f"    EXCELLENT balance ({ratio:.2f}x < 1.2)")
    elif ratio < 1.5:
        print(f"    VERY GOOD balance ({ratio:.2f}x < 1.5)")
    elif ratio < 2.0:
        print(f"     GOOD balance ({ratio:.2f}x < 2.0)")
    else:
        print(f"    IMBALANCED ({ratio:.2f}x >= 2.0)")
    
    # Check targets
    print(f"\n Target Check:")
    
    TARGETS = {
        "Rác thải": 1300,
        "Kim loại": 1300,
        "Pin": 1300,
        "Hộp giấy": 1300,
        "Nhựa": 1100,
        "Thủy tinh": 1100,
        "Hữu cơ": 1100,
        "Giấy": 900,
        "Vải": 900,
    }
    
    for class_name, target in TARGETS.items():
        actual = counts.get(class_name, 0)
        diff = actual - target
        if actual == 0:
            status = ""
        elif abs(diff) < 50:
            status = ""
        else:
            status = ""
        print(f"   {status} {class_name:12s}: {actual:5d} / {target:5d} ({diff:+4d})")
    
    print("\n" + "=" * 60)
    
    return counts, ratio

if __name__ == "__main__":
    from pathlib import Path
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Check train set
    print("\n Checking TRAIN set:")
    train_path = project_root / "yolo-dataset/train"
    
    if not train_path.exists():
        print(f"\n ERROR: yolo-dataset/train not found!")
        print(f"   Expected: {train_path}")
        print(f"\n Run these first:")
        print(f"   1. python 01_curate_textile.py")
        print(f"   2. python 02_curate_glass.py")
        print(f"   3. python 03_copy_other_classes.py")
        exit(1)
    
    train_counts, train_ratio = verify_distribution(str(train_path))
    
    if train_counts is None:
        print("\n Verification failed!")
        exit(1)
    
    print("\n Next steps:")
    if train_ratio and train_ratio < 1.5:
        print(" Distribution looks good!")
        print("1. Add real collection images (if not done)")
        print("2. Run augmentation: python 04_diversity_augmentation.py")
        print("3. Setup CVAT for annotation")
    else:
        print("  Check distribution above")
        print("1. Verify all classes copied correctly")
        print("2. Add real collection images")
        print("3. Run augmentation if ready")
