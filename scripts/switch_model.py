import shutil
import os
import datetime
from pathlib import Path

def switch_to_new_model():
    """
    Switch to the latest trained model.
    
    This script:
    1. Finds the latest training run (supports multiple naming patterns)
    2. Locates the best.pt model file
    3. Backs up the current model
    4. Copies the new model to models/yolov8s_best.pt
    """
    # Configuration
    # Use same path resolution as train_optimized.py
    PROJECT_ROOT = Path.home() / "waste-classification-vn"
    TRAINING_DIR = PROJECT_ROOT / "runs/detect"
    DESTINATION_DIR = PROJECT_ROOT / "models"
    MODEL_FILENAME = "yolov8s_best.pt"
    
    # Supported training run name patterns
    # Add more patterns here if you use different naming conventions
    TRAINING_PATTERNS = [
        'waste_production_v1',
        'waste_optimized_v1',
        'waste_production',
        'waste_optimized',
    ]
    
    print("=" * 70)
    print("🔄 SWITCHING TO NEW MODEL")
    print("=" * 70)
    
    # 1. Find the latest training run
    # Look for folders matching any of the patterns
    all_runs = []
    for pattern in TRAINING_PATTERNS:
        matching_runs = [d for d in TRAINING_DIR.iterdir() 
                        if d.is_dir() and pattern in d.name]
        all_runs.extend(matching_runs)
    
    # Also check nested runs/detect structure (YOLO sometimes creates this)
    nested_detect = TRAINING_DIR / "runs" / "detect"
    if nested_detect.exists():
        for pattern in TRAINING_PATTERNS:
            matching_runs = [d for d in nested_detect.iterdir() 
                            if d.is_dir() and pattern in d.name]
            all_runs.extend(matching_runs)
    
    if not all_runs:
        print("❌ No training runs found!")
        print(f"   Searched in: {TRAINING_DIR}")
        print(f"   Patterns: {', '.join(TRAINING_PATTERNS)}")
        return
    
    # Sort by modification time (newest first)
    # This ensures we always pick the most recently trained model
    runs = sorted(all_runs, key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Display all found runs
    print(f"\n📁 Found {len(runs)} training run(s):")
    for i, run in enumerate(runs[:5], 1):  # Show top 5
        mtime = datetime.datetime.fromtimestamp(run.stat().st_mtime)
        age = datetime.datetime.now() - mtime
        age_str = f"{age.days}d {age.seconds//3600}h ago" if age.days > 0 else f"{age.seconds//3600}h {age.seconds//60%60}m ago"
        marker = " ⭐ NEWEST" if i == 1 else ""
        print(f"   {i}. {run.name} (modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}, {age_str}){marker}")
    
    # Select the newest run (first in sorted list)
    latest_run = runs[0]
    print(f"\n✅ Selected: {latest_run.name} (most recently modified)")
    new_model_path = latest_run / "weights" / "best.pt"
    
    # Check if best.pt exists
    if not new_model_path.exists():
        print(f"\n❌ No best.pt found in {latest_run}")
        print(f"   Expected: {new_model_path}")
        if (latest_run / "weights").exists():
            weights_files = list((latest_run / "weights").glob("*.pt"))
            if weights_files:
                print(f"   Available files: {[f.name for f in weights_files]}")
        return
        
    # Get model info
    model_size_mb = new_model_path.stat().st_size / (1024 * 1024)
    print(f"\n✅ Found new model:")
    print(f"   Run: {latest_run.name}")
    print(f"   Path: {new_model_path}")
    print(f"   Size: {model_size_mb:.1f} MB")
    
    # 2. Backup existing model
    current_model = DESTINATION_DIR / MODEL_FILENAME
    if current_model.exists():
        current_size_mb = current_model.stat().st_size / (1024 * 1024)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = DESTINATION_DIR / f"yolov8s_backup_{timestamp}.pt"
        shutil.copy2(current_model, backup_path)
        print(f"\n💾 Backed up current model:")
        print(f"   From: {current_model.name} ({current_size_mb:.1f} MB)")
        print(f"   To: {backup_path.name}")
    else:
        print(f"\n⚠️  No existing model found at {current_model}")
        print(f"   This will be the first model installation.")
    
    # 3. Copy new model
    print(f"\n📋 Copying new model...")
    shutil.copy2(new_model_path, current_model)
    
    print("\n" + "=" * 70)
    print(" SUCCESS! New model installed.")
    print("=" * 70)
    print(f"   Location: {current_model}")
    print(f"   Size: {model_size_mb:.1f} MB")
    print(f"\n  IMPORTANT: Restart your backend server to load the new weights!")
    print("=" * 70)

if __name__ == "__main__":
    switch_to_new_model()
