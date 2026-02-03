"""Fix and Standardize Class Names in Roboflow Exports"""
from pathlib import Path
import yaml

# Standard Vietnamese class names
STANDARD_NAMES = {
    # Variations -> Standard
    'nhua': 'Nhựa',
    'Nhua': 'Nhựa',
    'plastic': 'Nhựa',
    
    'pin': 'Pin',
    'Pin': 'Pin',
    'battery': 'Pin',
    
    'vai': 'Vải',
    'Vai': 'Vải',
    'textile': 'Vải',
    'cloth': 'Vải',
    
    'kim_loai': 'Kim loại',
    'kim loai': 'Kim loại',
    'Kim_loai': 'Kim loại',
    'metal': 'Kim loại',
    
    'rac_thai': 'Rác thải',
    'rac thai': 'Rác thải',
    'Rac_thai': 'Rác thải',
    'trash': 'Rác thải',
    
    'thuy_tinh': 'Thủy tinh',
    'thuy tinh': 'Thủy tinh',
    'Thuy_tinh': 'Thủy tinh',
    'glass': 'Thủy tinh',
    
    'giay': 'Giấy',
    'Giay': 'Giấy',
    'paper': 'Giấy',
    
    'hop_giay': 'Hộp giấy',
    'hop giay': 'Hộp giấy',
    'Hop_giay': 'Hộp giấy',
    'cardboard': 'Hộp giấy',
    
    'huu_co': 'Hữu cơ',
    'huu co': 'Hữu cơ',
    'Huu_co': 'Hữu cơ',
    'organic': 'Hữu cơ',
    'biological': 'Hữu cơ',
    'objects': 'Hữu cơ',  # Fix the extra class
}

def fix_data_yaml(yaml_path):
    """Fix class names in a data.yaml file"""
    
    with open(yaml_path, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if 'names' not in data:
        print(f"     No 'names' field in {yaml_path}")
        return False
    
    original_names = data['names']
    
    # Standardize names
    fixed_names = []
    for name in original_names:
        standard_name = STANDARD_NAMES.get(name, name)
        if standard_name not in fixed_names:
            fixed_names.append(standard_name)
    
    # Update data
    data['names'] = fixed_names
    data['nc'] = len(fixed_names)
    
    # Save
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    
    if original_names != fixed_names:
        print(f"    Fixed: {original_names} → {fixed_names}")
        return True
    else:
        print(f"     OK: {fixed_names}")
        return False

def main():
    """Fix all data.yaml files in roboflow-exports"""
    
    BASE_DIR = Path.home() / "waste-classification-vn" / "roboflow-exports"
    
    print("=" * 60)
    print("FIX CLASS NAMES IN DATA.YAML FILES")
    print("=" * 60)
    
    print(f"\n Scanning: {BASE_DIR}")
    
    if not BASE_DIR.exists():
        print(f" Directory not found: {BASE_DIR}")
        return
    
    fixed_count = 0
    
    for folder in BASE_DIR.iterdir():
        if not folder.is_dir():
            continue
        
        yaml_path = folder / 'data.yaml'
        
        if not yaml_path.exists():
            print(f"\n  {folder.name}: No data.yaml")
            continue
        
        print(f"\n {folder.name}:")
        
        if fix_data_yaml(yaml_path):
            fixed_count += 1
    
    print("\n" + "=" * 60)
    print(" COMPLETE!")
    print("=" * 60)
    print(f"\n   Fixed: {fixed_count} files")
    print(f"\n Now re-run merge:")
    print(f"   cd ~/waste-classification-vn")
    print(f"   rm -rf yolo-dataset-merged")
    print(f"   python yolo-scripts/13_merge_roboflow_exports.py")

if __name__ == "__main__":
    main()
