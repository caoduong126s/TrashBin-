from pathlib import Path
import yaml
from collections import Counter
import matplotlib.pyplot as plt

def analyze_class_balance():
    # Load config
    data_yaml = Path('/Users/caoduong22102004gmail.com/waste-classification-vn/yolo-dataset-merged/data.yaml')
    with open(data_yaml) as f:
        data = yaml.safe_load(f)
    
    class_names = data['names']
    train_path = Path(data['path']) / 'labels' / 'train'
    
    print(f"Analyzing {train_path}...")
    
    # Count classes
    counts = Counter()
    total_labels = 0
    
    for label_file in train_path.glob('*.txt'):
        with open(label_file) as f:
            for line in f:
                cls_id = int(line.split()[0])
                counts[cls_id] += 1
                total_labels += 1
                
    print("\nClass Distribution:")
    print(f"{'ID':<3} {'Name':<15} {'Count':<8} {'Percentage':<10}")
    print("-" * 40)
    
    sorted_counts = sorted(counts.items())
    for cls_id, count in sorted_counts:
        name = class_names[cls_id] if cls_id < len(class_names) else "Unknown"
        percent = (count / total_labels) * 100
        print(f"{cls_id:<3} {name:<15} {count:<8} {percent:.1f}%")
        
    # Check "Nhua" dominance
    nhua_count = counts.get(0, 0)
    avg_count = total_labels / len(class_names)
    ratio = nhua_count / avg_count
    
    print("\nAnalysis:")
    if ratio > 1.5:
        print(f"  WARNING: 'Nhua' (ID 0) is {ratio:.1f}x more frequent than average.")
        print("   -> This explains why the model biases towards 'Nhua'!")
    else:
        print(" Class balance looks relatively healthy.")

if __name__ == "__main__":
    analyze_class_balance()
