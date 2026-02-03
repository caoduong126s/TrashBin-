"""
Copy Other Classes (No Curation Needed)
Works with data/processed/train/ (English names)
Maps to Vietnamese names in output
"""

import shutil
from pathlib import Path
from tqdm import tqdm

# Class name mapping (English → Vietnamese)
CLASS_MAPPING = {
    'plastic': 'Nhựa',
    'paper': 'Giấy',
    'cardboard': 'Hộp giấy',
    'metal': 'Kim loại',
    'battery': 'Pin',
    'biological': 'Hữu cơ',
    'trash': 'Rác thải'
}

def copy_class(english_name, vietnamese_name, input_base, output_base):
    """Copy all images from a class"""
    
    input_dir = Path(input_base) / english_name
    output_dir = Path(output_base) / vietnamese_name
    
    if not input_dir.exists():
        print(f"  {english_name}: Input directory not found: {input_dir}")
        return 0
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all images
    image_files = list(input_dir.glob('*.jpg')) + \
                  list(input_dir.glob('*.png')) + \
                  list(input_dir.glob('*.jpeg'))
    
    if len(image_files) == 0:
        print(f"  {english_name}: No images found")
        return 0
    
    # Copy all
    for img_path in tqdm(image_files, desc=f"Copying {english_name} → {vietnamese_name}"):
        shutil.copy2(img_path, output_dir / img_path.name)
    
    return len(image_files)

def main():
    """Copy all classes that don't need curation"""
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    INPUT_BASE = project_root / "data/processed/train"
    OUTPUT_BASE = project_root / "yolo-dataset/train"
    
    print("=" * 60)
    print("COPY OTHER CLASSES (No Curation)")
    print("=" * 60)
    print(f"\nInput:  {INPUT_BASE}")
    print(f"Output: {OUTPUT_BASE}")
    
    # Classes to copy (keep all) - skipping textile and glass (already curated)
    results = {}
    
    for english_name, vietnamese_name in CLASS_MAPPING.items():
        print(f"\n Processing: {english_name} → {vietnamese_name}")
        count = copy_class(english_name, vietnamese_name, INPUT_BASE, OUTPUT_BASE)
        results[vietnamese_name] = count
        if count > 0:
            print(f"    Copied: {count} images")
    
    # Summary
    print("\n" + "=" * 60)
    print(" COPY COMPLETE!")
    print("=" * 60)
    print("\n Summary:")
    for class_name, count in results.items():
        print(f"   {class_name:12s}: {count:4d} images")
    print(f"\n   TOTAL: {sum(results.values())} images")
    print("=" * 60)
    
    print("\n Next steps:")
    print("1. Verify all classes in: yolo-dataset/train/")
    print("2. Add your 620 real collection images")
    print("3. Run: python 04_diversity_augmentation.py")

if __name__ == "__main__":
    main()
