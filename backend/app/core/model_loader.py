"""
Model Loader for YOLOv8s

Handles loading and initializing the YOLO object detection model
"""

from ultralytics import YOLO
from pathlib import Path
from typing import Optional
import logging

import os
from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelLoader:
    """Singleton class for loading and managing the YOLO model"""
    
    _instance: Optional['ModelLoader'] = None
    _model: Optional[YOLO] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize model loader"""
        if self._model is None:
            self.load_model()
    
    def load_model(self) -> YOLO:
        """
        Load the trained YOLOv8s model
        
        Returns:
            Loaded YOLO model
        """
        try:
            # Current file: backend/app/core/model_loader.py
            current_file = Path(__file__).resolve()
            backend_dir = current_file.parent.parent.parent
            project_root = backend_dir.parent
            
            # Handle MODEL_PATH
            # If it's absolute, use it directly
            # If it's relative, we assume it's relative to project_root if it starts with ../ 
            # OR relative to backend_dir if it doesn't.
            # However, the config default is "../models/..." which implies relative to backend_dir but stepping out.
            
            # Let's verify the logic from the test script which worked:
            # model_relative = settings.MODEL_PATH.lstrip('../')
            # model_path = project_root / model_relative
            
            # Robust way:
            path_str = settings.MODEL_PATH
            if os.path.isabs(path_str):
                 model_path = Path(path_str)
            else:
                # Remove ../ prefix to get path from project root
                clean_path = path_str.replace('../', '').replace('./', '')
                model_path = project_root / clean_path
            
            model_path = model_path.resolve()
            
            logger.info(f"Looking for YOLO model at: {model_path}")
            logger.info(f"Current working directory: {os.getcwd()}")
            logger.info(f"User ID: {os.getuid()}")
            
            if not model_path.exists():
                logger.error(f" Model file not found at: {model_path}")
                logger.error(f"  > os.path.exists says: {os.path.exists(str(model_path))}")
                logger.error(f"  > Parent directory: {model_path.parent}")
                logger.error(f"  > Parent exists: {model_path.parent.exists()}")
                if model_path.parent.exists():
                    logger.error(f"  > Parent contents: {os.listdir(model_path.parent)}")
                else:
                    logger.error(f"  > Parent directory does not exist either!")

                # Try to find it in likely places as fallback
                fallback = project_root / "models" / "yolov8s_best.pt"
                if fallback.exists():
                    logger.warning(f"  Found model at fallback location: {fallback}")
                    model_path = fallback
                else:
                    raise FileNotFoundError(f"Model file not found: {model_path}")
            
            logger.info(f"Loading YOLO model from: {model_path}")
            
            # Load YOLO model
            model = YOLO(str(model_path))
            
            # Verify model loaded correctly
            if model is None:
                raise RuntimeError("Failed to load YOLO model")
            
            self._model = model
            
            logger.info("=" * 60)
            logger.info(" YOLO MODEL LOADED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info(f"Architecture: YOLOv8s")
            logger.info(f"Model path: {model_path}")
            logger.info(f"Number of classes: {len(model.names)}")
            logger.info(f"Class names: {list(model.names.values())}")
            logger.info(f"Confidence threshold: {settings.CONF_THRESHOLD}")
            logger.info(f"IOU threshold: {settings.IOU_THRESHOLD}")
            logger.info(f"Input size: {settings.IMAGE_SIZE}x{settings.IMAGE_SIZE}")
            logger.info("=" * 60)
            
            return model
            
        except Exception as e:
            logger.error(f"Error loading YOLO model: {str(e)}")
            raise
    
    @property
    def model(self) -> YOLO:
        """Get the loaded model"""
        if self._model is None:
            self.load_model()
        return self._model
    
    def reload_model(self) -> YOLO:
        """Reload the model (useful for hot-reload)"""
        logger.info("Reloading YOLO model...")
        self._model = None
        return self.load_model()
    
    def predict(
        self, 
        source,
        conf: Optional[float] = None,
        iou: Optional[float] = None,
        imgsz: Optional[int] = None,
        verbose: bool = False,
        stream: bool = False
    ):
        """
        Run prediction on source
        
        Args:
            source: Image path, numpy array, PIL image, or video source
            conf: Confidence threshold (default from settings)
            iou: IOU threshold for NMS (default from settings)
            imgsz: Input image size (default from settings)
            verbose: Show prediction details
            stream: Stream mode for video
            
        Returns:
            YOLO Results object
        """
        if self._model is None:
            self.load_model()
        
        return self._model.predict(
            source=source,
            conf=conf or settings.CONF_THRESHOLD,
            iou=iou or settings.IOU_THRESHOLD,
            imgsz=imgsz or settings.IMAGE_SIZE,
            verbose=verbose,
            stream=stream
        )


# Global instance
model_loader = ModelLoader()


def get_model() -> YOLO:
    """
    Get the loaded YOLO model instance
    
    Returns:
        Loaded YOLO model
    """
    return model_loader.model


def predict_image(source, **kwargs):
    """
    Convenience function for single image prediction
    
    Args:
        source: Image source
        **kwargs: Additional arguments for YOLO predict
        
    Returns:
        YOLO Results object
    """
    return model_loader.predict(source, **kwargs)


def reload_model() -> YOLO:
    """
    Reload the model
    
    Returns:
        Reloaded YOLO model
    """
    return model_loader.reload_model()