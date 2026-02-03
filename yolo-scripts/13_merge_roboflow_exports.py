"""Merge Multiple Roboflow Exports"""
import shutil
from pathlib import Path
import yaml
from collections import defaultdict

def merge_roboflow_exports(source_dirs, output_dir, train_val_split=True):
    print("=" * 60)
    print("MERGING ROBOFLOW EXPORTS")
    print("=" * 60)
    output_path = Path(output_dir)
    if train_val_split:
        dirs = {'train_images': output_path / 'images' / 'train', 'train_labels': output_path / 'labels' / 'train', 'val_images': output_path / 'images' / 'val', 'val_labels': output_path / 'labels' / 'val'}
    else:
        dirs = {'train_images': output_path / 'images' / 'train', 'train_labels': output_path / 'labels' / 'train'}
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    print(f"\n Created output structure")
    all_class_names = []
    class_mappings = {}
    print(f"\n Analyzing {len(source_dirs)} folders...")
    for source_dir in source_dirs:
        source_path = Path(source_dir)
        yaml_file = source_path / 'data.yaml'
        if not yaml_file.exists():
            continue
        with open(yaml_file, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        class_names = data['names']
        print(f"   {source_path.name}: {class_names}")
        for cls_name in class_names:
            if cls_name not in all_class_names:
                all_class_names.append(cls_name)
    print(f"\n  Unified classes ({len(all_class_names)}):")
    for i, name in enumerate(all_class_names):
        print(f"   {i}: {name}")
    for source_dir in source_dirs:
        source_path = Path(source_dir)
        yaml_file = source_path / 'data.yaml'
        if not yaml_file.exists():
            continue
        with open(yaml_file, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        mapping = {}
        for old_id, class_name in enumerate(data['names']):
            new_id = all_class_names.index(class_name)
            mapping[old_id] = new_id
        class_mappings[source_path.name] = mapping
    print(f"\n Copying files...")
    stats = defaultdict(lambda: {'images': 0, 'labels': 0})
    for source_dir in source_dirs:
        source_path = Path(source_dir)
        class_name = source_path.name
        print(f"\n    {class_name}")
        if class_name not in class_mappings:
            continue
        mapping = class_mappings[class_name]
        train_images = source_path / 'train' / 'images'
        train_labels = source_path / 'train' / 'labels'
        if train_images.exists() and train_labels.exists():
            for img_file in list(train_images.glob('*.jpg')) + list(train_images.glob('*.png')):
                dest_img = dirs['train_images'] / f"{class_name}_{img_file.name}"
                shutil.copy2(img_file, dest_img)
                stats[class_name]['images'] += 1
                label_file = train_labels / img_file.with_suffix('.txt').name
                if label_file.exists():
                    dest_label = dirs['train_labels'] / f"{class_name}_{label_file.name}"
                    with open(label_file) as f:
                        lines = f.readlines()
                    remapped = []
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) == 5:
                            old_id = int(parts[0])
                            new_id = mapping.get(old_id, old_id)
                            parts[0] = str(new_id)
                            remapped.append(' '.join(parts) + '\n')
                    with open(dest_label, 'w') as f:
                        f.writelines(remapped)
                    stats[class_name]['labels'] += 1
            print(f"       {stats[class_name]['images']} images")
        if train_val_split:
            val_images = source_path / 'valid' / 'images'
            val_labels = source_path / 'valid' / 'labels'
            if val_images.exists() and val_labels.exists():
                val_count = 0
                for img_file in list(val_images.glob('*.jpg')) + list(val_images.glob('*.png')):
                    dest_img = dirs['val_images'] / f"{class_name}_{img_file.name}"
                    shutil.copy2(img_file, dest_img)
                    label_file = val_labels / img_file.with_suffix('.txt').name
                    if label_file.exists():
                        dest_label = dirs['val_labels'] / f"{class_name}_{label_file.name}"
                        with open(label_file) as f:
                            lines = f.readlines()
                        remapped = []
                        for line in lines:
                            parts = line.strip().split()
                            if len(parts) == 5:
                                old_id = int(parts[0])
                                new_id = mapping.get(old_id, old_id)
                                parts[0] = str(new_id)
                                remapped.append(' '.join(parts) + '\n')
                        with open(dest_label, 'w') as f:
                            f.writelines(remapped)
                        val_count += 1
                if val_count > 0:
                    print(f"       {val_count} val")
    data_yaml = {'path': str(output_path.absolute()), 'train': 'images/train', 'val': 'images/val' if train_val_split else 'images/train', 'nc': len(all_class_names), 'names': all_class_names}
    yaml_path = output_path / 'data.yaml'
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data_yaml, f, allow_unicode=True, sort_keys=False)
    print(f"\n Created: {yaml_path}")
    print("\n" + "=" * 60)
    print(" COMPLETE!")
    print("=" * 60)
    total = sum(s['images'] for s in stats.values())
    print(f"\n   Total: {total} images, {len(all_class_names)} classes")
    return output_path

if __name__ == "__main__":
    import sys
    BASE_DIR = Path.home() / "waste-classification-vn" / "roboflow-exports"
    SOURCE_DIRS = [
        BASE_DIR / "Nhua",
        BASE_DIR / "Pin", 
        BASE_DIR / "Vai",
        BASE_DIR / "Kim_loai",
        BASE_DIR / "Rac_thai",
        BASE_DIR / "Thuy_tinh",
        BASE_DIR / "Giay",
        BASE_DIR / "Hop_giay",
        BASE_DIR / "Huu_co",
    ]
    OUTPUT_DIR = Path.home() / "waste-classification-vn" / "yolo-dataset-merged"
    print("\n" + "=" * 60)
    print("ROBOFLOW MERGER - FIXED")
    print("=" * 60)
    existing = [d for d in SOURCE_DIRS if d.exists()]
    print(f"\nFound {len(existing)} / {len(SOURCE_DIRS)} folders:")
    for d in existing:
        print(f"    {d.name}")
    if not existing:
        print("\n No folders!")
        sys.exit(1)
    response = input(f"\nMerge {len(existing)} folders? (yes/no): ").lower()
    if response not in ['yes', 'y']:
        sys.exit(0)
    merge_roboflow_exports(existing, OUTPUT_DIR, True)
    print(f"\n Done! Dataset at: {OUTPUT_DIR}")
