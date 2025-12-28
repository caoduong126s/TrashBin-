# src/manual_download_organizer.py

"""
Organize manually downloaded dataset
"""

import os
import zipfile
import shutil
from pathlib import Path
from sklearn.model_selection import train_test_split
import random
from tqdm import tqdm

class ManualDatasetOrganizer:
    """
    Organize dataset from manual download
    """
    
    def __init__(self, data_root='data'):
        self.data_root = Path(data_root)
        self.raw_dir = self.data_root / 'raw'
        self.temp_dir = self.data_root / 'temp'
        
        # Create directories
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_from_downloads(self, zip_path=None):
        """
        Extract dataset from Downloads folder
        """
        print("╔════════════════════════════════════════════════════════╗")
        print("║       MANUAL DATASET EXTRACTION                        ║")
        print("╚════════════════════════════════════════════════════════╝")
        print()
        
        # Auto-find zip file if not provided
        if zip_path is None:
            downloads_dir = Path.home() / 'Downloads'
            
            print(f"🔍 Searching for dataset in: {downloads_dir}")
            
            # Look for garbage/waste related zips
            zip_files = list(downloads_dir.glob('*garbage*.zip'))
            zip_files += list(downloads_dir.glob('*waste*.zip'))
            zip_files += list(downloads_dir.glob('*trash*.zip'))
            
            if not zip_files:
                print("\n❌ No dataset zip file found in Downloads/")
                print("\n💡 Please download dataset from:")
                print("   https://www.kaggle.com/datasets/mostafaabla/garbage-classification")
                print("\n   Then run again, or specify path:")
                print("   python src/manual_download_organizer.py /path/to/dataset.zip")
                return False
            
            # Use most recent
            zip_path = max(zip_files, key=os.path.getctime)
            print(f"✅ Found: {zip_path.name}")
        else:
            zip_path = Path(zip_path)
            
            if not zip_path.exists():
                print(f"❌ File not found: {zip_path}")
                return False
        
        print(f"\n📦 Extracting: {zip_path.name}")
        
        # Extract
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                for file in tqdm(file_list, desc="Extracting"):
                    zip_ref.extract(file, self.temp_dir)
            
            print("✅ Extraction completed!")
            return True
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return False
    
    def find_dataset_root(self):
        """
        Find where the actual images are
        Different datasets have different structures
        """
        print("\n🔍 Locating dataset root...")
        
        # Common patterns
        possible_roots = [
            self.temp_dir,
            self.temp_dir / 'Garbage classification',
            self.temp_dir / 'garbage-classification',
            self.temp_dir / 'dataset',
            self.temp_dir / 'data',
        ]
        
        # Also search subdirectories
        for subdir in self.temp_dir.rglob('*'):
            if subdir.is_dir():
                # Check if it has image folders
                subdirs = [d for d in subdir.iterdir() if d.is_dir()]
                
                if len(subdirs) >= 4:  # Likely has class folders
                    possible_roots.append(subdir)
        
        # Find the one with most class folders
        best_root = None
        max_classes = 0
        
        for root in possible_roots:
            if not root.exists():
                continue
            
            class_dirs = [d for d in root.iterdir() if d.is_dir()]
            
            # Check if folders contain images
            has_images = False
            for class_dir in class_dirs:
                images = list(class_dir.glob('*.jpg')) + list(class_dir.glob('*.png'))
                if images:
                    has_images = True
                    break
            
            if has_images and len(class_dirs) > max_classes:
                best_root = root
                max_classes = len(class_dirs)
        
        if best_root:
            print(f"✅ Dataset root: {best_root}")
            print(f"   Found {max_classes} class folders")
            return best_root
        else:
            print("❌ Could not locate dataset root")
            print("\n📁 Contents of temp directory:")
            for item in self.temp_dir.rglob('*'):
                if item.is_dir():
                    print(f"   {item.relative_to(self.temp_dir)}/")
            return None
    
    def organize_structure(self, dataset_root):
        """
        Organize into train/val/test
        """
        print("\n📁 Organizing dataset structure...")
        
        # Get all class folders
        class_dirs = [d for d in dataset_root.iterdir() if d.is_dir()]
        
        if not class_dirs:
            print("❌ No class folders found")
            return False
        
        print(f"Found {len(class_dirs)} classes: {[d.name for d in class_dirs]}")
        
        # Set seed for reproducibility
        random.seed(42)
        
        # Process each class
        for class_dir in tqdm(class_dirs, desc="Processing classes"):
            class_name = class_dir.name
            
            # Get all images
            image_files = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.PNG']:
                image_files.extend(list(class_dir.glob(ext)))
            
            if not image_files:
                print(f"\n⚠️  No images found in {class_name}")
                continue
            
            # Shuffle
            random.shuffle(image_files)
            
            # Split: 70% train, 15% val, 15% test
            train_files, temp_files = train_test_split(
                image_files, test_size=0.3, random_state=42
            )
            val_files, test_files = train_test_split(
                temp_files, test_size=0.5, random_state=42
            )
            
            # Create class directories
            for split in ['train', 'val', 'test']:
                split_class_dir = self.raw_dir / split / class_name
                split_class_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy files
            for img_file in train_files:
                shutil.copy2(img_file, self.raw_dir / 'train' / class_name / img_file.name)
            
            for img_file in val_files:
                shutil.copy2(img_file, self.raw_dir / 'val' / class_name / img_file.name)
            
            for img_file in test_files:
                shutil.copy2(img_file, self.raw_dir / 'test' / class_name / img_file.name)
        
        print("\n✅ Organization completed!")
        return True
    
    def verify_dataset(self):
        """
        Verify dataset structure
        """
        print("\n🔍 Verifying dataset...")
        
        splits = ['train', 'val', 'test']
        total_counts = {'train': 0, 'val': 0, 'test': 0}
        
        # Get classes from train folder
        train_dir = self.raw_dir / 'train'
        
        if not train_dir.exists():
            print("❌ Train directory not found")
            return False
        
        classes = [d.name for d in train_dir.iterdir() if d.is_dir()]
        
        if not classes:
            print("❌ No classes found")
            return False
        
        print(f"\n📊 Dataset Statistics:")
        print(f"{'Class':<15} {'Train':<10} {'Val':<10} {'Test':<10} {'Total':<10}")
        print("-" * 60)
        
        for class_name in sorted(classes):
            counts = {}
            
            for split in splits:
                class_dir = self.raw_dir / split / class_name
                if class_dir.exists():
                    count = len(list(class_dir.glob('*.*')))
                    counts[split] = count
                    total_counts[split] += count
                else:
                    counts[split] = 0
            
            total = sum(counts.values())
            print(f"{class_name:<15} {counts['train']:<10} {counts['val']:<10} {counts['test']:<10} {total:<10}")
        
        print("-" * 60)
        print(f"{'TOTAL':<15} {total_counts['train']:<10} {total_counts['val']:<10} {total_counts['test']:<10} {sum(total_counts.values()):<10}")
        
        # Check if we have data
        total = sum(total_counts.values())
        
        if total == 0:
            print("\n❌ No images found!")
            return False
        else:
            print(f"\n✅ Dataset ready: {total} total images")
            return True
    
    def cleanup_temp(self):
        """
        Remove temporary files
        """
        print("\n🧹 Cleaning up temporary files...")
        
        try:
            shutil.rmtree(self.temp_dir)
            print("✅ Cleanup completed!")
        except Exception as e:
            print(f"⚠️  Cleanup failed: {e}")
    
    def run_full_pipeline(self, zip_path=None):
        """
        Run complete pipeline
        """
        print("="*60)
        print("MANUAL DATASET ORGANIZATION PIPELINE")
        print("="*60)
        print()
        
        # Step 1: Extract
        if not self.extract_from_downloads(zip_path):
            return False
        
        # Step 2: Find dataset root
        dataset_root = self.find_dataset_root()
        if not dataset_root:
            return False
        
        # Step 3: Organize
        if not self.organize_structure(dataset_root):
            return False
        
        # Step 4: Verify
        if not self.verify_dataset():
            return False
        
        # Step 5: Cleanup
        self.cleanup_temp()
        
        print("\n" + "="*60)
        print("✅ DATASET READY!")
        print(f"📁 Location: {self.raw_dir.absolute()}")
        print("="*60)
        
        return True

# ============ MAIN EXECUTION ============

def main():
    """
    Main function
    """
    import sys
    
    organizer = ManualDatasetOrganizer()
    
    # Check if zip path provided as argument
    zip_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Check if dataset already exists
    if (organizer.raw_dir / 'train').exists():
        print("⚠️  Dataset already exists in data/raw/")
        response = input("Do you want to re-organize? (y/n): ")
        
        if response.lower() != 'y':
            print("Skipping.")
            organizer.verify_dataset()
            return
    
    # Run pipeline
    success = organizer.run_full_pipeline(zip_path)
    
    if success:
        print("\n🎉 Success! You can now proceed to Phase 2: EDA")
    else:
        print("\n❌ Failed! Please check errors above.")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure you downloaded the dataset from Kaggle")
        print("   2. ZIP file should be in Downloads/ folder")
        print("   3. Or specify path: python src/manual_download_organizer.py /path/to/file.zip")

if __name__ == '__main__':
    main()