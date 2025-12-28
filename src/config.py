# src/config.py

import yaml
from pathlib import Path

class Config:
    """Load and manage configuration"""
    
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def __getitem__(self, key):
        return self.config[key]
    
    def get(self, *keys, default=None):
        """Get nested config values"""
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
        return value if value is not None else default

# Usage example
if __name__ == '__main__':
    cfg = Config()
    print(f"Project: {cfg['project']['name']}")
    print(f"Batch size: {cfg.get('data', 'batch_size')}")
    print(f"Learning rate: {cfg.get('training', 'phase1', 'learning_rate')}")