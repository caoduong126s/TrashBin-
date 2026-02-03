import os
import yaml
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def get_yolo_stats(dataset_path):
    dataset_path = Path(dataset_path)
    yaml_file = dataset_path / 'data.yaml'
    if not yaml_file.exists():
        return None
    
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    
    class_names = data['names']
    counts = {name: 0 for name in class_names}
    
    # Check all labels
    label_dir = dataset_path / 'labels'
    for split in ['train', 'val']:
        split_dir = label_dir / split
        if split_dir.exists():
            for label_file in split_dir.glob('*.txt'):
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        parts = line.strip().split()
                        if parts:
                            cls_id = int(parts[0])
                            if cls_id < len(class_names):
                                counts[class_names[cls_id]] += 1
                                
    return counts

def main():
    # 1. Raw Data Stats (from 01_eda.ipynb analysis of data/raw)
    # Mapping raw classes to final YOLO classes for comparison
    # biological -> biological
    # battery -> battery
    # cardboard -> cardboard
    # metal -> metal
    # paper -> paper
    # plastic -> plastic
    # trash -> trash
    # brown-glass, green-glass, white-glass -> glass
    # clothes, shoes -> textile
    
    raw_stats = {
        'battery': 945,
        'biological': 985,
        'cardboard': 891,
        'glass': 607 + 629 + 775, # brown + green + white
        'metal': 769,
        'paper': 1050,
        'plastic': 865,
        'textile': 5325 + 1977, # clothes + shoes
        'trash': 697
    }
    
    # 2. Curated Data Stats (from yolo-dataset-merged)
    dataset_path = "/Users/caoduong22102004gmail.com/waste-classification-vn/yolo-dataset-merged"
    curated_counts_vn = get_yolo_stats(dataset_path)
    
    if not curated_counts_vn:
        print(f"Error: Could not find dataset at {dataset_path}")
        return

    # Map VN names back to English for comparison
    vn_to_en = {
        'Nhua': 'plastic',
        'Pin': 'battery',
        'Vai': 'textile',
        'Kim loai': 'metal',
        'Rac thai': 'trash',
        'Thuy tinh': 'glass',
        'Giay': 'paper',
        'Hop giay': 'cardboard',
        'Huu co': 'biological'
    }
    
    curated_counts = {vn_to_en.get(k, k): v for k, v in curated_counts_vn.items()}

    # Prepare DataFrame for plotting
    data = []
    all_classes = sorted(list(raw_stats.keys()))
    
    for cls in all_classes:
        data.append({
            'Lớp': cls.capitalize(),
            'Giai đoạn': 'Dữ liệu Thô (Raw)',
            'Số lượng': raw_stats.get(cls, 0)
        })
        data.append({
            'Lớp': cls.capitalize(),
            'Giai đoạn': 'Sau khi Làm sạch (Curated)',
            'Số lượng': curated_counts.get(cls, 0)
        })
        
    df = pd.DataFrame(data)
    
    # Plotting
    plt.figure(figsize=(14, 8))
    import seaborn as sns
    sns.set_style("whitegrid")
    
    # Bar plot
    ax = sns.barplot(x='Lớp', y='Số lượng', hue='Giai đoạn', data=df, palette=['#FF9999', '#4CAF50'])
    
    plt.title('So sánh Số lượng Mẫu trước và sau khi Làm sạch (Curation Impact)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Loại Rác Thải', fontsize=12)
    plt.ylabel('Số lượng Mẫu (Instances)', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(title='Trạng thái')
    
    # Add growth labels
    for i, cls in enumerate(all_classes):
        before = raw_stats.get(cls, 0)
        after = curated_counts.get(cls, 0)
        if before > 0:
            growth = ((after - before) / before) * 100
            color = 'green' if growth >= 0 else 'red'
            ax.text(i, max(before, after) + 100, f"{growth:+.1f}%", ha='center', fontsize=10, fontweight='bold', color=color)

    plt.tight_layout()
    
    # Save output
    output_dir = Path("/Users/caoduong22102004gmail.com/waste-classification-vn/docs/images")
    output_dir.mkdir(parents=True, exist_ok=True)
    save_path = output_dir / "curation_impact_eda.png"
    plt.savefig(save_path, dpi=300)
    
    print(f"\nEDA Visualization saved to: {save_path}")
    print("\nChi tiết so sánh (Growth Analysis):")
    print("-" * 50)
    print(f"{'Class':12} | {'Raw':8} | {'Curated':8} | {'Growth'}")
    print("-" * 50)
    for cls in all_classes:
        before = raw_stats.get(cls, 0)
        after = curated_counts.get(cls, 0)
        growth = ((after-before)/before)*100
        print(f"{cls:12} | {before:8} | {after:8} | {growth:+.1f}%")

if __name__ == "__main__":
    main()
