from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List
import os

# Resolve paths
# config.py is in backend/app/core/
CURRENT_FILE = Path(__file__).resolve()
BACKEND_DIR = CURRENT_FILE.parent.parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "yolov8s_best.pt"

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    API_TITLE: str = "GreenSort API"
    API_DESCRIPTION: str = "AI-powered waste classification system"
    API_VERSION: str = "2.0.0"
    
    # Model Settings - YOLO
    MODEL_PATH: str = str(DEFAULT_MODEL_PATH)
    MODEL_NAME: str = "yolov8s"
    MODEL_TYPE: str = "yolo"
    NUM_CLASSES: int = 9
    
    # YOLO Inference Settings
    CONF_THRESHOLD: float = 0.25
    IOU_THRESHOLD: float = 0.45
    IMAGE_SIZE: int = 640
    
    # Class-specific confidence thresholds (Lower = more sensitive)
    # These help prioritize classes that are harder to detect or under-represented
    CLASS_SPECIFIC_CONF: dict = {
        "biological": 0.23,  # Organic waste (High Sensitivity)
        "paper": 0.23,       # Paper (High Sensitivity)
        "cardboard": 0.24,   # Cardboard
        "metal": 0.25,
        "glass": 0.25,
        "plastic": 0.25,
        "battery": 0.28,     # Batteries (Slightly higher for precision)
        "textile": 0.25,
        "trash": 0.25
    }
    
    # Class-specific bounding box size constraints
    # Key: English class name
    # max_area: Maximum allowed area ratio (0.0 - 1.0) of the frame (640x480)
    # min_aspect: Minimum aspect ratio (width/height)
    # max_aspect: Maximum aspect ratio (width/height)
    CLASS_SIZE_CONSTRAINTS: dict = {
        "battery": {
            "max_area": 0.15,      # Small
            "min_aspect": 0.3, "max_aspect": 3.0 
        },
        "metal": {
            "max_area": 0.45,
            "min_aspect": 0.2, "max_aspect": 4.0
        },
        "biological": {
            "max_area": 0.50
        },
        "paper": {
            "max_area": 0.70
        },
        "cardboard": {
            "max_area": 0.65,
            "min_aspect": 0.4, "max_aspect": 2.5
        },
        "plastic": {
            "max_area": 0.50,
            "min_aspect": 0.2, "max_aspect": 3.0 # Bottles
        },
        "glass": {
            "max_area": 0.45,
            "min_aspect": 0.2, "max_aspect": 3.0 # Bottles
        },
        "textile": {
            "max_area": 0.60
        },
        "trash": {
            "max_area": 0.45
        }
    }
    
    # Device Settings (GPU acceleration if available)
    DEVICE: str = "cpu"  # Options: "cpu", "cuda", "mps" (Mac GPU)
    
    # Low-Light Mode Settings
    ENABLE_LOW_LIGHT_MODE: bool = True
    LOW_LIGHT_BRIGHTNESS_THRESHOLD: float = 80.0
    LOW_LIGHT_METHOD: str = "clahe"  # Options: "clahe", "gamma", "both"
    
    # Class Names (English)
    CLASS_NAMES: List[str] = [
        "battery",
        "biological", 
        "cardboard",
        "glass",
        "metal",
        "paper",
        "plastic",
        "textile",
        "trash"
    ]
    
    # Class Names (Vietnamese)
    CLASS_NAMES_VN: dict = {
        "battery": "Pin",
        "biological": "Huu co",
        "cardboard": "Hop giay",
        "glass": "Thuy tinh",
        "metal": "Kim loai",
        "paper": "Giay",
        "plastic": "Nhua",
        "textile": "Vai",
        "trash": "Rac thai"
    }
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # File Upload Settings
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp"]
    
    # Legacy Settings (kept for backward compatibility)
    CONFIDENCE_THRESHOLD_HIGH: float = 0.7
    CONFIDENCE_THRESHOLD_LOW: float = 0.4
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Database Configuration
    DB_TYPE: str = "sqlite"
    
    # MySQL Settings
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "greensort"
    
    # SQLite Settings
    SQLITE_PATH: str = "data/greensort.db"
    
    # Debug mode
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()