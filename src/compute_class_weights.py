"""
CLASS WEIGHTS CALCULATOR
========================
Calculate class weights to handle imbalanced dataset during training.
Uses inverse frequency weighting strategy.
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_DIR = Path('data/processed')
OUTPUT_DIR = Path('data/processed')

print("="*70)
print("CLASS WEIGHTS CALCULATION")
print("="*70)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def count_samples_per_class(data_dir, split='train'):
    """
    Count number of samples per class in training set
    """
    print(f"\n Counting samples in {split}/ split...")
    
    split_dir = data_dir / split
    
    if not split_dir.exists():
        print(f" ERROR: {split}/ directory not found")
        return None
    
    class_counts = {}
    
    # Get all class directories
    class_dirs = sorted([d for d in split_dir.iterdir() if d.is_dir()])
    
    for class_dir in class_dirs:
        class_name = class_dir.name
        
        # Skip hidden directories
        if class_name.startswith('.'):
            continue
        
        # Count images
        n_images = 0
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
            n_images += len(list(class_dir.glob(ext)))
        
        class_counts[class_name] = n_images
        print(f"   {class_name:<15s}: {n_images:>6,} images")
    
    return class_counts


def calculate_weights_inverse_frequency(class_counts):
    """
    Calculate class weights using inverse frequency method
    
    Formula: weight_i = total_samples / (n_classes * count_i)
    
    This gives higher weights to minority classes
    """
    print("\n Calculating inverse frequency weights...")
    
    total_samples = sum(class_counts.values())
    n_classes = len(class_counts)
    
    weights = {}
    
    for class_name, count in class_counts.items():
        weight = total_samples / (n_classes * count)
        weights[class_name] = weight
    
    return weights


def calculate_weights_effective_number(class_counts, beta=0.9999):
    """
    Calculate class weights using effective number of samples method
    
    Formula: weight_i = (1 - beta) / (1 - beta^n_i)
    
    Reference: "Class-Balanced Loss Based on Effective Number of Samples"
    https://arxiv.org/abs/1901.05555
    """
    print(f"\n Calculating effective number weights (beta={beta})...")
    
    weights = {}
    
    for class_name, count in class_counts.items():
        effective_num = (1.0 - beta) / (1.0 - np.power(beta, count))
        weights[class_name] = effective_num
    
    # Normalize weights
    total_weight = sum(weights.values())
    for class_name in weights:
        weights[class_name] = weights[class_name] / total_weight * len(weights)
    
    return weights


def calculate_weights_sqrt(class_counts):
    """
    Calculate class weights using square root method
    
    Formula: weight_i = sqrt(median_count / count_i)
    
    This is a softer reweighting strategy
    """
    print("\n Calculating square root weights...")
    
    counts = np.array(list(class_counts.values()))
    median_count = np.median(counts)
    
    weights = {}
    
    for class_name, count in class_counts.items():
        weight = np.sqrt(median_count / count)
        weights[class_name] = weight
    
    return weights


def normalize_weights(weights):
    """
    Normalize weights so minimum weight is 1.0
    """
    min_weight = min(weights.values())
    
    normalized = {}
    for class_name, weight in weights.items():
        normalized[class_name] = weight / min_weight
    
    return normalized


def display_weights(weights, class_counts, title="Class Weights"):
    """
    Display calculated weights in a formatted table
    """
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(f"\n{'Class':<15s} {'Samples':>10s} {'Weight':>12s} {'Normalized':>12s}")
    print("-" * 70)
    
    # Sort by weight (descending)
    sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
    
    # Normalize
    normalized = normalize_weights(weights)
    
    for class_name, weight in sorted_weights:
        count = class_counts[class_name]
        norm_weight = normalized[class_name]
        print(f"{class_name:<15s} {count:>10,} {weight:>12.4f} {norm_weight:>12.2f}×")
    
    print("-" * 70)
    print(f"\n Interpretation:")
    print(f"   - Higher weight = Minority class (model will focus more)")
    print(f"   - Lower weight = Majority class (model will focus less)")
    print(f"   - Normalized: relative to smallest weight (1.0×)")


def convert_to_keras_format(weights, class_to_idx):
    """
    Convert class weights to Keras format: {class_idx: weight}
    """
    keras_weights = {}
    
    for class_name, weight in weights.items():
        idx = class_to_idx[class_name]
        keras_weights[idx] = float(weight)
    
    return keras_weights


def save_weights(weights, class_counts, output_dir):
    """
    Save calculated weights to JSON file
    """
    # Create class to index mapping (sorted alphabetically)
    classes = sorted(class_counts.keys())
    class_to_idx = {name: idx for idx, name in enumerate(classes)}
    idx_to_class = {idx: name for name, idx in class_to_idx.items()}
    
    # Convert to different formats
    inverse_freq_keras = convert_to_keras_format(weights['inverse_frequency'], class_to_idx)
    effective_num_keras = convert_to_keras_format(weights['effective_number'], class_to_idx)
    sqrt_keras = convert_to_keras_format(weights['sqrt'], class_to_idx)
    
    # Prepare output
    output = {
        'class_to_idx': class_to_idx,
        'idx_to_class': idx_to_class,
        'num_classes': len(classes),
        'class_counts': class_counts,
        'weights': {
            'inverse_frequency': {
                'description': 'Inverse frequency weighting: weight_i = total / (n_classes * count_i)',
                'class_weights': weights['inverse_frequency'],
                'keras_format': inverse_freq_keras,
                'normalized': normalize_weights(weights['inverse_frequency'])
            },
            'effective_number': {
                'description': 'Effective number of samples: weight_i = (1-beta) / (1-beta^n_i), beta=0.9999',
                'class_weights': weights['effective_number'],
                'keras_format': effective_num_keras,
                'normalized': normalize_weights(weights['effective_number'])
            },
            'sqrt': {
                'description': 'Square root weighting: weight_i = sqrt(median / count_i)',
                'class_weights': weights['sqrt'],
                'keras_format': sqrt_keras,
                'normalized': normalize_weights(weights['sqrt'])
            }
        },
        'recommendation': {
            'method': 'inverse_frequency',
            'reason': 'Most commonly used, good balance between over/under-weighting'
        }
    }
    
    # Save to file
    output_path = output_dir / 'class_weights.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Class weights saved to: {output_path}")
    
    # Also save a simple version for quick use
    simple_output = {
        'class_to_idx': class_to_idx,
        'recommended_weights': inverse_freq_keras
    }
    
    simple_path = output_dir / 'class_weights_simple.json'
    with open(simple_path, 'w', encoding='utf-8') as f:
        json.dump(simple_output, f, indent=2)
    
    print(f" Simple weights saved to: {simple_path}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function
    """
    # Check data directory
    if not DATA_DIR.exists():
        print(f" ERROR: Data directory not found: {DATA_DIR}")
        print(f"   Please run merge_classes.py first!")
        return
    
    # Count samples per class
    class_counts = count_samples_per_class(DATA_DIR, split='train')
    
    if class_counts is None:
        return
    
    # Calculate weights using different methods
    weights = {}
    
    # Method 1: Inverse frequency (recommended)
    weights['inverse_frequency'] = calculate_weights_inverse_frequency(class_counts)
    display_weights(weights['inverse_frequency'], class_counts, 
                   "Method 1: Inverse Frequency Weighting (RECOMMENDED)")
    
    # Method 2: Effective number
    weights['effective_number'] = calculate_weights_effective_number(class_counts, beta=0.9999)
    display_weights(weights['effective_number'], class_counts,
                   "Method 2: Effective Number of Samples")
    
    # Method 3: Square root
    weights['sqrt'] = calculate_weights_sqrt(class_counts)
    display_weights(weights['sqrt'], class_counts,
                   "Method 3: Square Root Weighting")
    
    # Save weights
    save_weights(weights, class_counts, OUTPUT_DIR)
    
    # Final summary
    print("\n" + "="*70)
    print("CLASS WEIGHTS CALCULATION COMPLETED!")
    print("="*70)
    print(f"\n Calculated weights for {len(class_counts)} classes")
    print(f" Total training samples: {sum(class_counts.values()):,}")
    print(f"\n Recommendation:")
    print(f"   Use 'inverse_frequency' method for most cases")
    print(f"   Load weights from: class_weights_simple.json")
    print(f"\n Usage in training:")
    print(f"   import json")
    print(f"   with open('data/processed/class_weights_simple.json') as f:")
    print(f"       weights = json.load(f)['recommended_weights']")
    print(f"   model.fit(..., class_weight=weights)")
    print("\n Ready for Step 3.3: Augmentation Pipeline!")
    print("="*70)


if __name__ == '__main__':
    main()
