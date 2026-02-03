"""
Feedback API Endpoints
Allows users to provide feedback on classification results
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import logging

from app.core.database import get_db
from app.models.feedback import ClassificationFeedback
from app.core.config import settings

router = APIRouter(prefix="/feedback", tags=["feedback"])
logger = logging.getLogger(__name__)


class FeedbackRequest(BaseModel):
    """Request model for feedback submission"""
    classification_id: Optional[int] = None
    is_correct: bool
    correct_class: Optional[str] = None
    user_comment: Optional[str] = None
    user_id: str = "anonymous"


@router.post("/submit")
async def submit_feedback(
    feedback: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """
    Submit feedback on a classification result
    
    Args:
        feedback: Feedback data
        db: Database session
        
    Returns:
        Success message and feedback ID
    """
    try:
        # Validate correct_class if provided
        if feedback.correct_class and feedback.correct_class not in settings.CLASS_NAMES:
            # Check Vietnamese names
            if feedback.correct_class not in settings.CLASS_NAMES_VN.values():
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid class name. Must be one of: {settings.CLASS_NAMES}"
                )
        
        # Create feedback entry
        db_feedback = ClassificationFeedback(
            classification_id=feedback.classification_id,
            is_correct=feedback.is_correct,
            correct_class=feedback.correct_class,
            user_comment=feedback.user_comment,
            user_id=feedback.user_id
        )
        
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        logger.info(f" Feedback submitted: ID={db_feedback.id}, is_correct={feedback.is_correct}")
        
        return {
            "success": True,
            "message": "Cảm ơn bạn đã đóng góp phản hồi!",
            "feedback_id": db_feedback.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" Error submitting feedback: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi gửi phản hồi: {str(e)}"
        )


@router.get("/stats")
async def get_feedback_stats(
    db: Session = Depends(get_db)
):
    """
    Get feedback statistics
    
    Returns:
        Statistics about user feedback
    """
    try:
        total_feedback = db.query(ClassificationFeedback).count()
        correct_count = db.query(ClassificationFeedback).filter(
            ClassificationFeedback.is_correct == True
        ).count()
        incorrect_count = db.query(ClassificationFeedback).filter(
            ClassificationFeedback.is_correct == False
        ).count()
        
        accuracy = (correct_count / total_feedback * 100) if total_feedback > 0 else 0
        
        return {
            "success": True,
            "data": {
                "total_feedback": total_feedback,
                "correct_count": correct_count,
                "incorrect_count": incorrect_count,
                "accuracy_rate": round(accuracy, 2)
            }
        }
        
    except Exception as e:
        logger.error(f" Error getting feedback stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy thống kê: {str(e)}"
        )


@router.get("/recent")
async def get_recent_feedback(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent feedback entries
    
    Args:
        limit: Number of entries to return
        
    Returns:
        List of recent feedback
    """
    try:
        feedback_list = db.query(ClassificationFeedback)\
            .order_by(ClassificationFeedback.created_at.desc())\
            .limit(limit)\
            .all()
        
        return {
            "success": True,
            "data": [
                {
                    "id": fb.id,
                    "classification_id": fb.classification_id,
                    "is_correct": fb.is_correct,
                    "correct_class": fb.correct_class,
                    "user_comment": fb.user_comment,
                    "user_id": fb.user_id,
                    "created_at": fb.created_at.isoformat() if fb.created_at else None
                }
                for fb in feedback_list
            ]
        }
        
    except Exception as e:
        logger.error(f" Error getting recent feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy phản hồi: {str(e)}"
        )
