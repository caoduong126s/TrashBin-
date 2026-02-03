"""
Crowdsourcing API Endpoints
Allows users to submit images to expand the dataset
"""

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from pathlib import Path
from PIL import Image
import io
import logging
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.models.crowdsource import CrowdsourcedImage
from app.core.config import settings

router = APIRouter(prefix="/crowdsource", tags=["crowdsource"])
logger = logging.getLogger(__name__)

# Upload directory
UPLOAD_DIR = Path(__file__).parent.parent.parent.parent / "uploads" / "crowdsourced"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/submit")
async def submit_crowdsourced_image(
    file: UploadFile = File(...),
    user_label: str = Form(...),
    user_id: str = Form("anonymous"),
    db: Session = Depends(get_db)
):
    """
    Submit an image with label for dataset expansion
    
    Args:
        file: Image file
        user_label: User's classification label
        user_id: User identifier
        db: Database session
        
    Returns:
        Success message and submission ID
    """
    try:
        # Validate label
        if user_label not in settings.CLASS_NAMES:
            # Check Vietnamese names
            if user_label not in settings.CLASS_NAMES_VN.values():
                raise HTTPException(
                    status_code=400,
                    detail=f"Nhãn không hợp lệ. Phải là một trong: {list(settings.CLASS_NAMES_VN.values())}"
                )
        
        # Validate file extension
        file_ext = f".{file.filename.split('.')[-1].lower()}"
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Định dạng file không hợp lệ. Chỉ chấp nhận: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Read and validate image
        contents = await file.read()
        
        if len(contents) > settings.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File quá lớn. Kích thước tối đa: {settings.MAX_IMAGE_SIZE / 1024 / 1024:.1f}MB"
            )
        
        try:
            image = Image.open(io.BytesIO(contents))
            if image.mode != 'RGB':
                image = image.convert('RGB')
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Không thể đọc file ảnh: {str(e)}"
            )
        
        # Create directory for this class
        class_dir = UPLOAD_DIR / user_label
        class_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{user_id}_{timestamp}{file_ext}"
        file_path = class_dir / filename
        
        # Save image
        image.save(file_path)
        
        # Save to database
        db_entry = CrowdsourcedImage(
            image_path=str(file_path.relative_to(UPLOAD_DIR.parent)),
            user_label=user_label,
            user_id=user_id,
            verified=False
        )
        
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        
        logger.info(f" Crowdsourced image submitted: ID={db_entry.id}, label={user_label}")
        
        return {
            "success": True,
            "message": "Cảm ơn bạn đã đóng góp ảnh! Ảnh của bạn sẽ được xem xét.",
            "submission_id": db_entry.id,
            "label": user_label
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" Error submitting crowdsourced image: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi gửi ảnh: {str(e)}"
        )


@router.get("/stats")
async def get_crowdsource_stats(
    db: Session = Depends(get_db)
):
    """
    Get crowdsourcing statistics
    
    Returns:
        Statistics about submitted images
    """
    try:
        total_images = db.query(CrowdsourcedImage).count()
        verified_images = db.query(CrowdsourcedImage).filter(
            CrowdsourcedImage.verified == True
        ).count()
        pending_images = total_images - verified_images
        
        # Count by class
        class_counts = {}
        for class_name in settings.CLASS_NAMES_VN.values():
            count = db.query(CrowdsourcedImage).filter(
                CrowdsourcedImage.user_label == class_name
            ).count()
            if count > 0:
                class_counts[class_name] = count
        
        return {
            "success": True,
            "data": {
                "total_images": total_images,
                "verified_images": verified_images,
                "pending_images": pending_images,
                "class_distribution": class_counts
            }
        }
        
    except Exception as e:
        logger.error(f" Error getting crowdsource stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy thống kê: {str(e)}"
        )


@router.get("/images")
async def get_crowdsourced_images(
    verified: Optional[bool] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get list of crowdsourced images (for admin review)
    
    Args:
        verified: Filter by verification status
        limit: Number of entries to return
        
    Returns:
        List of submitted images
    """
    try:
        query = db.query(CrowdsourcedImage)
        
        if verified is not None:
            query = query.filter(CrowdsourcedImage.verified == verified)
        
        images = query.order_by(CrowdsourcedImage.created_at.desc()).limit(limit).all()
        
        return {
            "success": True,
            "data": [
                {
                    "id": img.id,
                    "image_path": img.image_path,
                    "user_label": img.user_label,
                    "user_id": img.user_id,
                    "verified": img.verified,
                    "admin_comment": img.admin_comment,
                    "created_at": img.created_at.isoformat() if img.created_at else None
                }
                for img in images
            ]
        }
        
    except Exception as e:
        logger.error(f" Error getting crowdsourced images: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy danh sách ảnh: {str(e)}"
        )
