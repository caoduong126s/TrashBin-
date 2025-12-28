"""
DATA GENERATORS FOR TRAINING
=============================
Create TensorFlow/Keras data generators with:
- Differential augmentation per class
- Class weights integration
- Train/Val/Test generators
"""

import json
import numpy as np
from pathlib import Path
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import tensorflow as tf

# Suppress TensorFlow warnings
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("="*70)
print("DATA GENERATORS SETUP")
print("="*70)

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_DIR = Path('data/processed')
IMG_SIZE = 224
BATCH_SIZE = 32

# ============================================================================
# LOAD CONFIGURATIONS
# ============================================================================

def load_configs(data_dir):
    """Load augmentation config and class weights"""
    print("\n Loading configurations...")
    
    # Load augmentation config
    aug_config_path = data_dir / 'augmentation_config.json'
    with open(aug_config_path, 'r') as f:
        aug_config = json.load(f)
    print(f" Loaded augmentation config: {aug_config_path}")
    
    # Load class weights
    weights_path = data_dir / 'class_weights_simple.json'
    with open(weights_path, 'r') as f:
        weights_data = json.load(f)
    print(f" Loaded class weights: {weights_path}")
    
    return aug_config, weights_data


# ============================================================================
# CREATE GENERATORS
# ============================================================================

def create_train_generator(data_dir, batch_size=32, seed=42):
    """
    Create training data generator with augmentation
    
    Uses ImageDataGenerator with standard augmentations.
    For differential augmentation, we use class weights during training.
    """
    print("\n Creating TRAINING generator...")
    
    # Define augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        brightness_range=[0.8, 1.2],
        fill_mode='nearest'
    )
    
    # Create generator
    train_generator = train_datagen.flow_from_directory(
        directory=str(data_dir / 'train'),
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=True,
        seed=seed
    )
    
    print(f" Training generator created")
    print(f"   Classes: {len(train_generator.class_indices)}")
    print(f"   Samples: {train_generator.samples}")
    print(f"   Batch size: {batch_size}")
    print(f"   Steps per epoch: {len(train_generator)}")
    
    return train_generator


def create_val_generator(data_dir, batch_size=32, seed=42):
    """
    Create validation data generator (no augmentation)
    """
    print("\n Creating VALIDATION generator...")
    
    # No augmentation for validation
    val_datagen = ImageDataGenerator(
        rescale=1./255
    )
    
    # Create generator
    val_generator = val_datagen.flow_from_directory(
        directory=str(data_dir / 'val'),
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=False,  # Don't shuffle validation data
        seed=seed
    )
    
    print(f" Validation generator created")
    print(f"   Classes: {len(val_generator.class_indices)}")
    print(f"   Samples: {val_generator.samples}")
    print(f"   Batch size: {batch_size}")
    print(f"   Steps per epoch: {len(val_generator)}")
    
    return val_generator


def create_test_generator(data_dir, batch_size=32, seed=42):
    """
    Create test data generator (no augmentation, no shuffle)
    """
    print("\n Creating TEST generator...")
    
    # No augmentation for test
    test_datagen = ImageDataGenerator(
        rescale=1./255
    )
    
    # Create generator
    test_generator = test_datagen.flow_from_directory(
        directory=str(data_dir / 'test'),
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=False,  # NEVER shuffle test data
        seed=seed
    )
    
    print(f"   Test generator created")
    print(f"   Classes: {len(test_generator.class_indices)}")
    print(f"   Samples: {test_generator.samples}")
    print(f"   Batch size: {batch_size}")
    print(f"   Steps: {len(test_generator)}")
    
    return test_generator


# ============================================================================
# GENERATOR TESTING
# ============================================================================

def test_generators(train_gen, val_gen, test_gen):
    """
    Test generators to ensure they work correctly
    """
    print("\n" + "="*70)
    print(" TESTING GENERATORS")
    print("="*70)
    
    # Test training generator
    print("\n  Testing training generator...")
    try:
        batch_x, batch_y = next(train_gen)
        print(f"    Batch shape: {batch_x.shape}")
        print(f"    Labels shape: {batch_y.shape}")
        print(f"    Pixel range: [{batch_x.min():.3f}, {batch_x.max():.3f}]")
        print(f"    Classes in batch: {batch_y.sum(axis=0).astype(int).tolist()}")
    except Exception as e:
        print(f"    ERROR: {e}")
        return False
    
    # Test validation generator
    print("\n  Testing validation generator...")
    try:
        batch_x, batch_y = next(val_gen)
        print(f"    Batch shape: {batch_x.shape}")
        print(f"    Labels shape: {batch_y.shape}")
        print(f"    Pixel range: [{batch_x.min():.3f}, {batch_x.max():.3f}]")
    except Exception as e:
        print(f"    ERROR: {e}")
        return False
    
    # Test test generator
    print("\n  Testing test generator...")
    try:
        batch_x, batch_y = next(test_gen)
        print(f"    Batch shape: {batch_x.shape}")
        print(f"    Labels shape: {batch_y.shape}")
        print(f"    Pixel range: [{batch_x.min():.3f}, {batch_x.max():.3f}]")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    # Verify class mappings are consistent
    print("\n  Verifying class mappings...")
    if (train_gen.class_indices == val_gen.class_indices == test_gen.class_indices):
        print(f"    Class mappings are consistent across all generators")
    else:
        print(f"    ERROR: Class mappings are inconsistent!")
        return False
    
    print("\n All generator tests passed!")
    return True


# ============================================================================
# DISPLAY INFO
# ============================================================================

def display_generator_info(train_gen, val_gen, test_gen, weights_data):
    """
    Display comprehensive information about generators
    """
    print("\n" + "="*70)
    print(" GENERATOR INFORMATION")
    print("="*70)
    
    # Class mapping
    print("\n Class Mapping:")
    class_indices = train_gen.class_indices
    print(f"{'Class Name':<15s} {'Index':>6s} {'Train':>8s} {'Val':>8s} {'Test':>8s}")
    print("-" * 70)
    
    for class_name in sorted(class_indices.keys()):
        idx = class_indices[class_name]
        
        # Count samples per class
        train_count = sum(1 for y in train_gen.labels if y == idx)
        val_count = sum(1 for y in val_gen.labels if y == idx)
        test_count = sum(1 for y in test_gen.labels if y == idx)
        
        print(f"{class_name:<15s} {idx:>6d} {train_count:>8d} {val_count:>8d} {test_count:>8d}")
    
    print("-" * 70)
    print(f"{'TOTAL':<15s} {'':<6s} {train_gen.samples:>8d} {val_gen.samples:>8d} {test_gen.samples:>8d}")
    
    # Class weights
    print("\n  Class Weights (for training):")
    recommended_weights = weights_data['recommended_weights']
    print(f"{'Index':>6s} {'Class Name':<15s} {'Weight':>10s}")
    print("-" * 70)
    for idx_str, weight in sorted(recommended_weights.items(), key=lambda x: int(x[0])):
        idx = int(idx_str)
        class_name = [k for k, v in class_indices.items() if v == idx][0]
        print(f"{idx:>6d} {class_name:<15s} {weight:>10.4f}")
    
    # Summary statistics
    print("\n Summary:")
    print(f"   Total images: {train_gen.samples + val_gen.samples + test_gen.samples:,}")
    print(f"   Number of classes: {len(class_indices)}")
    print(f"   Image size: {IMG_SIZE}×{IMG_SIZE}")
    print(f"   Batch size: {BATCH_SIZE}")
    print(f"   Training steps/epoch: {len(train_gen)}")
    print(f"   Validation steps/epoch: {len(val_gen)}")
    print(f"   Test steps: {len(test_gen)}")


# ============================================================================
# SAVE GENERATOR CONFIG
# ============================================================================

def save_generator_config(train_gen, weights_data, output_dir):
    """
    Save generator configuration for use in training scripts
    """
    config = {
        'image_size': IMG_SIZE,
        'batch_size': BATCH_SIZE,
        'num_classes': len(train_gen.class_indices),
        'class_indices': train_gen.class_indices,
        'class_weights': weights_data['recommended_weights'],
        'training_samples': train_gen.samples,
        'steps_per_epoch': len(train_gen),
        'augmentation': {
            'rotation_range': 20,
            'width_shift_range': 0.2,
            'height_shift_range': 0.2,
            'shear_range': 0.2,
            'zoom_range': 0.2,
            'horizontal_flip': True,
            'brightness_range': [0.8, 1.2]
        }
    }
    
    output_path = output_dir / 'generator_config.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n Generator config saved to: {output_path}")


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
        return
    
    # Load configurations
    aug_config, weights_data = load_configs(DATA_DIR)
    
    # Create generators
    train_gen = create_train_generator(DATA_DIR, batch_size=BATCH_SIZE)
    val_gen = create_val_generator(DATA_DIR, batch_size=BATCH_SIZE)
    test_gen = create_test_generator(DATA_DIR, batch_size=BATCH_SIZE)
    
    # Test generators
    success = test_generators(train_gen, val_gen, test_gen)
    
    if not success:
        print("\n Generator tests failed!")
        return
    
    # Display information
    display_generator_info(train_gen, val_gen, test_gen, weights_data)
    
    # Save configuration
    save_generator_config(train_gen, weights_data, DATA_DIR)
    
    # Final summary
    print("\n" + "="*70)
    print(" DATA GENERATORS READY!")
    print("="*70)
    print("\n Usage in training script:")
    print("""
    import json
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    
    # Load class weights
    with open('data/processed/class_weights_simple.json') as f:
        weights = json.load(f)['recommended_weights']
    
    # Convert to integer keys for Keras
    class_weights = {int(k): v for k, v in weights.items()}
    
    # Load generators (same as above)
    train_gen = create_train_generator('data/processed', batch_size=32)
    val_gen = create_val_generator('data/processed', batch_size=32)
    
    # Train model
    model.fit(
        train_gen,
        validation_data=val_gen,
        class_weight=class_weights,
        epochs=50,
        callbacks=[...]
    )
    """)
    
    print("\n PHASE 3 COMPLETED! Ready for Phase 4: Model Training! 🚀")
    print("="*70)


if __name__ == '__main__':
    main()
