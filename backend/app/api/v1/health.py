"""
Health Check Endpoint - YOLO Version
"""

from fastapi import APIRouter
from datetime import datetime

from app.core.config import settings
from app.core.model_loader import get_model

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns system status and YOLO model information
    """
    try:
        # Check if model is loaded
        model = get_model()
        model_loaded = model is not None
        
        # Get YOLO device info
        device = str(model.device) if model else 'cpu'
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "model": {
                "loaded": model_loaded,
                "type": "YOLOv8s",
                "name": settings.MODEL_NAME,
                "num_classes": len(model.names) if model else settings.NUM_CLASSES,
                "class_names": list(model.names.values()) if model else [],
                "device": device,
                "conf_threshold": settings.CONF_THRESHOLD,
                "iou_threshold": settings.IOU_THRESHOLD,
                "image_size": settings.IMAGE_SIZE
            },
            "api": {
                "version": settings.API_VERSION,
                "environment": settings.ENVIRONMENT
            },
            "capabilities": {
                "multiple_objects": True,
                "bounding_boxes": True,
                "realtime_detection": True
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GreenSort API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health"
    }