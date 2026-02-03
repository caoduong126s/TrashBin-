from ultralytics import YOLO
from pathlib import Path
import torch
import yaml
import os

def train_optimized():
    print("=" * 60)
    print(" STARTING OPTIMIZED TRAINING (Scene Diversity Fix)")
    print("=" * 60)

    # 1. Setup Config
    DATA_YAML = Path.home() / "waste-classification-vn" / "yolo-dataset-merged" / "data.yaml"
    if not DATA_YAML.exists():
        print(f" Error: {DATA_YAML} not found!")
        return

    # 2. Check Device
    device = 'cpu'
    if torch.cuda.is_available():
        device = 0
        print(f" GPU Detected: {torch.cuda.get_device_name(0)}")
    elif torch.backends.mps.is_available():
        device = 'mps'
        print(" Apple Metal (MPS) Detected")
    else:
        print(" No GPU detected. Training on CPU (Slow)")

    # 3. Load Model
    model = YOLO('yolov8s.pt')
    print(" Model loaded: YOLOv8s")

    # 4. Train with OPTIMIZED settings
    print("\n  Applying Robust Augmentations:")
    print("   mosaic=1.0     (Active)")
    print("   mixup=0.2      (Active - Fixes simple background filtering)")
    print("   copy_paste=0.1 (Active - Simulates clutter)")
    print("   degrees=20.0   (Active - Higher rotation)")

    results = model.train(
        # Data
        data=str(DATA_YAML),
        
        # Training
        epochs=150,
        patience=25,
        imgsz=640,
        batch=16 if device != 'cpu' else 4,
        
        # Hardware
        device=device,
        workers=8,
        
        # Project
        project='runs/detect',
        name='waste_optimized_v1',
        exist_ok=True,
        pretrained=True,
        
        # === KEY OPTIMIZATIONS ===
        mosaic=1.0,
        mixup=0.2,          # ENABLED
        copy_paste=0.1,     # ENABLED
        degrees=20.0,       # Increased
        scale=0.6,          # Increased
        perspective=0.0005, # Mild perspective
        hsv_h=0.02,         # Richer color variation
        
        # Hyperparameters
        lr0=0.01,
        optimizer='SGD',
        cos_lr=True,
        
        # Settings
        verbose=True,
        seed=42,
        save=True,
        plots=True
    )

    print("\n Training Complete!")
    print(f"Results saved to: {results.save_dir}")

if __name__ == "__main__":
    train_optimized()
