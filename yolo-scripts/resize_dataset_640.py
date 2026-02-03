import cv2
import os
from pathlib import Path
from tqdm import tqdm

def resize_images(input_dir, output_dir, size=(640, 640)):
    """
    Resize all images in input_dir (and subdirs) to size and save to output_dir
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory structure
    for subdir in ['train', 'val']:
        (output_path / 'images' / subdir).mkdir(parents=True, exist_ok=True)
        (output_path / 'labels' / subdir).mkdir(parents=True, exist_ok=True)

    # Copy data.yaml if exists
    if (input_path / 'data.yaml').exists():
        import shutil
        shutil.copy2(input_path / 'data.yaml', output_path / 'data.yaml')
        print(f"Copied data.yaml to {output_path}")

    # Process images
    for split in ['train', 'val']:
        img_dir = input_path / 'images' / split
        if not img_dir.exists():
            print(f"Warning: {img_dir} does not exist. Skipping.")
            continue
            
        label_src_dir = input_path / 'labels' / split
        label_dst_dir = output_path / 'labels' / split
        
        # Copy labels (nothing to change as they are normalized 0-1)
        if label_src_dir.exists():
            import shutil
            for label_file in label_src_dir.glob('*.txt'):
                shutil.copy2(label_file, label_dst_dir / label_file.name)
            print(f"Copied {split} labels.")

        images = list(img_dir.glob('*.jpg')) + list(img_dir.glob('*.png')) + list(img_dir.glob('*.jpeg'))
        print(f"Resizing {len(images)} images in {split}...")
        
        for img_file in tqdm(images):
            try:
                img = cv2.imread(str(img_file))
                if img is None:
                    print(f"Error reading {img_file}")
                    continue
                    
                resized = cv2.resize(img, size, interpolation=cv2.INTER_LINEAR)
                
                # Save to output dir
                out_file = output_path / 'images' / split / img_file.name
                cv2.imwrite(str(out_file), resized)
            except Exception as e:
                print(f"Failed to process {img_file}: {e}")

if __name__ == "__main__":
    BASE_DIR = Path("/Users/caoduong22102004gmail.com/waste-classification-vn")
    INPUT_DATASET = BASE_DIR / "yolo-dataset-merged"
    OUTPUT_DATASET = BASE_DIR / "yolo-dataset-640"
    
    print(f"Starting resizing process...")
    print(f"Input: {INPUT_DATASET}")
    print(f"Output: {OUTPUT_DATASET}")
    
    resize_images(INPUT_DATASET, OUTPUT_DATASET)
    
    print(f"\nDone! Normalized dataset created at: {OUTPUT_DATASET}")
