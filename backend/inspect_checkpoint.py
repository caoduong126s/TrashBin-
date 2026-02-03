#!/usr/bin/env python3
"""Inspect model checkpoint to determine exact architecture"""

import torch
from collections import OrderedDict

# Load checkpoint
checkpoint_path = '../models/efficientnet_b0_best_optimized.pth'
checkpoint = torch.load(checkpoint_path, map_location='cpu')

print("=" * 80)
print(" CHECKPOINT INSPECTION")
print("=" * 80)

# Check checkpoint structure
if isinstance(checkpoint, dict):
    print(f"\n Checkpoint type: dict")
    print(f" Keys in checkpoint: {list(checkpoint.keys())}")
    
    if 'model_state_dict' in checkpoint:
        state_dict = checkpoint['model_state_dict']
        print(f" Found 'model_state_dict'")
    elif 'state_dict' in checkpoint:
        state_dict = checkpoint['state_dict']
        print(f" Found 'state_dict'")
    else:
        state_dict = checkpoint
        print(f" Using checkpoint directly as state_dict")
    
    # Print other keys if present
    for key in checkpoint.keys():
        if key not in ['model_state_dict', 'state_dict']:
            print(f"   - {key}: {checkpoint[key]}")
else:
    state_dict = checkpoint
    print(f"\n Checkpoint type: OrderedDict/state_dict directly")

# Analyze classifier layers
print("\n" + "=" * 80)
print(" CLASSIFIER LAYERS ANALYSIS")
print("=" * 80)

classifier_keys = [k for k in state_dict.keys() if k.startswith('classifier.')]
classifier_keys.sort()

print(f"\n Found {len(classifier_keys)} classifier parameters:\n")

for key in classifier_keys:
    param = state_dict[key]
    print(f"  {key:40} → Shape: {str(param.shape):25}")

# Try to infer architecture
print("\n" + "=" * 80)
print("  INFERRED CLASSIFIER ARCHITECTURE")
print("=" * 80)

print("\n Based on the parameter shapes, the classifier likely has:")
print("\n nn.Sequential(")

layer_num = 0
for key in classifier_keys:
    if 'weight' in key and 'running' not in key:
        shape = state_dict[key].shape
        layer_idx = key.split('.')[1]
        
        if 'Linear' in str(type(shape)) or len(shape) == 2:
            print(f"    {layer_idx}: nn.Linear({shape[1]}, {shape[0]}),")
        
    elif 'bias' in key and 'running' not in key:
        continue  # Skip, already handled with weight
        
    elif 'running_mean' in key:
        shape = state_dict[key].shape
        layer_idx = key.split('.')[1]
        print(f"    {layer_idx}: nn.BatchNorm1d({shape[0]}),")

print(" )")

# Check specific layers
print("\n" + "=" * 80)
print(" KEY FINDINGS")
print("=" * 80)

# Check classifier.1 (first linear layer)
if 'classifier.1.weight' in state_dict:
    shape = state_dict['classifier.1.weight'].shape
    print(f"\n classifier.1 (Linear): {shape[1]} → {shape[0]}")
    
# Check classifier.3 (could be BatchNorm)
if 'classifier.3.weight' in state_dict:
    shape = state_dict['classifier.3.weight'].shape
    print(f" classifier.3 (BatchNorm1d): {shape[0]} features")
    
# Check final layer
last_linear = max([k for k in classifier_keys if 'weight' in k and 'running' not in k])
final_shape = state_dict[last_linear].shape
print(f" {last_linear} (Final Linear): {final_shape[1]} → {final_shape[0]} classes")

print("\n" + "=" * 80)
print(" INSPECTION COMPLETE")
print("=" * 80)

# Print suggested model creation code
print("\n SUGGESTED MODEL CREATION CODE:")
print("\n```python")
print("model = models.efficientnet_b0(weights=None)")
print("num_features = 1280  # EfficientNet-B0 features")
print()
print("model.classifier = nn.Sequential(")

for key in sorted(classifier_keys):
    if 'weight' in key and 'running' not in key:
        shape = state_dict[key].shape
        layer_idx = key.split('.')[1]
        
        if len(shape) == 2:  # Linear layer
            print(f"    nn.Linear({shape[1]}, {shape[0]}),  # classifier.{layer_idx}")
    elif 'running_mean' in key:
        shape = state_dict[key].shape
        layer_idx = key.split('.')[1]
        print(f"    nn.BatchNorm1d({shape[0]}),  # classifier.{layer_idx}")

print(")")
print("```")