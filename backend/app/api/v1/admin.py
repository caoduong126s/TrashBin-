"""
Admin API Endpoints for Feedback Management
Provides comprehensive admin functionality to view, filter, and analyze user feedback
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from typing import Optional, List, Literal
from datetime import datetime, timedelta
import logging
import csv
import io
import json

from app.core.database import get_db
from app.models.feedback import ClassificationFeedback
from app.core.config import settings

router = APIRouter(prefix="/admin/feedback", tags=["admin"])
logger = logging.getLogger(__name__)

# TODO: Add authentication middleware here for production
# Example: @router.get("/all", dependencies=[Depends(verify_admin_token)])
# For now, endpoints are open as requested


# NOTE: Specific routes must be defined BEFORE parameterized routes like /{feedback_id}
# to avoid route conflicts


@router.get("/all")
async def get_all_feedback(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    is_correct: Optional[bool] = Query(None, description="Filter by correctness"),
    class_name: Optional[str] = Query(None, description="Filter by class name"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO format)"),
    sort_by: Literal["created_at", "id"] = Query("created_at", description="Sort field"),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort order"),
    db: Session = Depends(get_db)
):
    """
    Get all feedback with pagination and filtering
    
    Admin endpoint to retrieve all user feedback with comprehensive filtering options.
    Supports pagination, date range filtering, class filtering, and sorting.
    
    Returns:
        Paginated list of feedback entries with metadata
    """
    try:
        # Build query with filters
        query = db.query(ClassificationFeedback)
        
        # Apply filters
        if is_correct is not None:
            query = query.filter(ClassificationFeedback.is_correct == is_correct)
        
        if class_name:
            # Filter by either correct_class or look up in classification history
            query = query.filter(ClassificationFeedback.correct_class == class_name)
        
        if user_id:
            query = query.filter(ClassificationFeedback.user_id.like(f"%{user_id}%"))
        
        if start_date:
            query = query.filter(ClassificationFeedback.created_at >= start_date)
        
        if end_date:
            # Add one day to include the end date
            end_date_inclusive = end_date + timedelta(days=1)
            query = query.filter(ClassificationFeedback.created_at < end_date_inclusive)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply sorting
        sort_column = getattr(ClassificationFeedback, sort_by)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        offset = (page - 1) * limit
        feedback_list = query.offset(offset).limit(limit).all()
        
        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit  # Ceiling division
        
        return {
            "success": True,
            "data": {
                "feedback": [
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
                ],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total_items": total_count,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting all feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy danh sách phản hồi: {str(e)}"
        )


@router.get("/by-class")
async def get_feedback_by_class(
    db: Session = Depends(get_db)
):
    """
    Get feedback statistics grouped by class
    
    Returns breakdown of correct/incorrect feedback for each waste class.
    Useful for identifying which classes have the most misclassifications.
    
    Returns:
        Dictionary with class-wise feedback statistics
    """
    try:
        # Get all feedback with correct_class specified
        feedback_with_class = db.query(
            ClassificationFeedback.correct_class,
            ClassificationFeedback.is_correct,
            func.count(ClassificationFeedback.id).label('count')
        ).filter(
            ClassificationFeedback.correct_class.isnot(None)
        ).group_by(
            ClassificationFeedback.correct_class,
            ClassificationFeedback.is_correct
        ).all()
        
        # Organize by class
        class_stats = {}
        for class_name, is_correct, count in feedback_with_class:
            if class_name not in class_stats:
                class_stats[class_name] = {
                    "class_name": class_name,
                    "correct_count": 0,
                    "incorrect_count": 0,
                    "total": 0
                }
            
            if is_correct:
                class_stats[class_name]["correct_count"] = count
            else:
                class_stats[class_name]["incorrect_count"] = count
            
            class_stats[class_name]["total"] += count
        
        # Calculate accuracy for each class
        for class_name in class_stats:
            total = class_stats[class_name]["total"]
            correct = class_stats[class_name]["correct_count"]
            class_stats[class_name]["accuracy_rate"] = round(
                (correct / total * 100) if total > 0 else 0, 2
            )
        
        return {
            "success": True,
            "data": {
                "by_class": list(class_stats.values()),
                "total_classes": len(class_stats)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting feedback by class: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy thống kê theo loại: {str(e)}"
        )


@router.get("/analytics")
async def get_feedback_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    group_by: Optional[Literal["day", "week", "month"]] = Query(None, description="Group by time period"),
    db: Session = Depends(get_db)
):
    """
    Get detailed feedback analytics
    
    Provides comprehensive analytics including:
    - Total feedback count
    - Accuracy rate over time
    - Most misclassified classes
    - User engagement metrics
    - Common correction patterns
    
    Returns:
        Detailed analytics data
    """
    try:
        # Build base query
        query = db.query(ClassificationFeedback)
        
        # Apply date filters
        if start_date:
            query = query.filter(ClassificationFeedback.created_at >= start_date)
        if end_date:
            end_date_inclusive = end_date + timedelta(days=1)
            query = query.filter(ClassificationFeedback.created_at < end_date_inclusive)
        
        # Get all feedback in range
        all_feedback = query.all()
        total_feedback = len(all_feedback)
        
        if total_feedback == 0:
            return {
                "success": True,
                "data": {
                    "total_feedback": 0,
                    "accuracy_rate": 0,
                    "correct_count": 0,
                    "incorrect_count": 0,
                    "message": "Không có dữ liệu phản hồi trong khoảng thời gian này"
                }
            }
        
        # Calculate basic stats
        correct_count = sum(1 for fb in all_feedback if fb.is_correct)
        incorrect_count = total_feedback - correct_count
        accuracy_rate = round((correct_count / total_feedback * 100), 2)
        
        # Get most misclassified classes
        misclassifications = {}
        for fb in all_feedback:
            if not fb.is_correct and fb.correct_class:
                if fb.correct_class not in misclassifications:
                    misclassifications[fb.correct_class] = 0
                misclassifications[fb.correct_class] += 1
        
        most_misclassified = sorted(
            [{"class": k, "count": v} for k, v in misclassifications.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:5]  # Top 5
        
        # User engagement
        unique_users = len(set(fb.user_id for fb in all_feedback if fb.user_id))
        avg_feedback_per_user = round(total_feedback / unique_users, 2) if unique_users > 0 else 0
        
        # Feedback with comments
        feedback_with_comments = sum(1 for fb in all_feedback if fb.user_comment)
        comment_rate = round((feedback_with_comments / total_feedback * 100), 2)
        
        # Time series data (if group_by specified)
        time_series = None
        if group_by:
            time_series = _generate_time_series(all_feedback, group_by)
        
        return {
            "success": True,
            "data": {
                "overview": {
                    "total_feedback": total_feedback,
                    "correct_count": correct_count,
                    "incorrect_count": incorrect_count,
                    "accuracy_rate": accuracy_rate
                },
                "misclassifications": {
                    "most_misclassified": most_misclassified,
                    "total_unique_misclassified": len(misclassifications)
                },
                "user_engagement": {
                    "unique_users": unique_users,
                    "avg_feedback_per_user": avg_feedback_per_user,
                    "feedback_with_comments": feedback_with_comments,
                    "comment_rate": comment_rate
                },
                "time_series": time_series
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy phân tích: {str(e)}"
        )


def _generate_time_series(feedback_list: List[ClassificationFeedback], group_by: str):
    """Helper function to generate time series data"""
    from collections import defaultdict
    
    time_buckets = defaultdict(lambda: {"total": 0, "correct": 0, "incorrect": 0})
    
    for fb in feedback_list:
        if not fb.created_at:
            continue
        
        # Determine bucket key based on group_by
        if group_by == "day":
            bucket_key = fb.created_at.strftime("%Y-%m-%d")
        elif group_by == "week":
            # ISO week format
            bucket_key = fb.created_at.strftime("%Y-W%W")
        else:  # month
            bucket_key = fb.created_at.strftime("%Y-%m")
        
        time_buckets[bucket_key]["total"] += 1
        if fb.is_correct:
            time_buckets[bucket_key]["correct"] += 1
        else:
            time_buckets[bucket_key]["incorrect"] += 1
    
    # Calculate accuracy for each bucket
    result = []
    for period, stats in sorted(time_buckets.items()):
        accuracy = round((stats["correct"] / stats["total"] * 100), 2) if stats["total"] > 0 else 0
        result.append({
            "period": period,
            "total": stats["total"],
            "correct": stats["correct"],
            "incorrect": stats["incorrect"],
            "accuracy_rate": accuracy
        })
    
    return result


@router.get("/export")
async def export_feedback(
    format: Literal["json", "csv"] = Query("json", description="Export format"),
    is_correct: Optional[bool] = Query(None, description="Filter by correctness"),
    class_name: Optional[str] = Query(None, description="Filter by class name"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db)
):
    """
    Export feedback data as CSV or JSON
    
    Allows downloading all feedback data in CSV or JSON format with optional filtering.
    Useful for external analysis or backup purposes.
    
    Returns:
        Downloadable file (CSV or JSON)
    """
    try:
        # Build query with same filters as /all endpoint
        query = db.query(ClassificationFeedback)
        
        if is_correct is not None:
            query = query.filter(ClassificationFeedback.is_correct == is_correct)
        if class_name:
            query = query.filter(ClassificationFeedback.correct_class == class_name)
        if start_date:
            query = query.filter(ClassificationFeedback.created_at >= start_date)
        if end_date:
            end_date_inclusive = end_date + timedelta(days=1)
            query = query.filter(ClassificationFeedback.created_at < end_date_inclusive)
        
        # Get all matching feedback
        feedback_list = query.order_by(desc(ClassificationFeedback.created_at)).all()
        
        if format == "csv":
            # Generate CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "ID", "Classification ID", "Is Correct", "Correct Class",
                "User Comment", "User ID", "Created At"
            ])
            
            # Write data
            for fb in feedback_list:
                writer.writerow([
                    fb.id,
                    fb.classification_id or "",
                    "Yes" if fb.is_correct else "No",
                    fb.correct_class or "",
                    fb.user_comment or "",
                    fb.user_id or "anonymous",
                    fb.created_at.isoformat() if fb.created_at else ""
                ])
            
            # Return as downloadable CSV
            output.seek(0)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=feedback_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                }
            )
        
        else:  # JSON format
            data = [
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
            
            json_str = json.dumps({
                "success": True,
                "exported_at": datetime.now().isoformat(),
                "total_records": len(data),
                "data": data
            }, indent=2, ensure_ascii=False)
            
            return StreamingResponse(
                iter([json_str]),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=feedback_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                }
            )
        
    except Exception as e:
        logger.error(f"❌ Error exporting feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xuất dữ liệu: {str(e)}"
        )


@router.get("/{feedback_id}")
async def get_feedback_detail(
    feedback_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific feedback entry
    
    Returns full details of a single feedback entry including
    related classification data if available.
    
    Args:
        feedback_id: ID of the feedback entry
        
    Returns:
        Detailed feedback information
    """
    try:
        feedback = db.query(ClassificationFeedback).filter(
            ClassificationFeedback.id == feedback_id
        ).first()
        
        if not feedback:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy phản hồi với ID {feedback_id}"
            )
        
        return {
            "success": True,
            "data": {
                "id": feedback.id,
                "classification_id": feedback.classification_id,
                "is_correct": feedback.is_correct,
                "correct_class": feedback.correct_class,
                "user_comment": feedback.user_comment,
                "user_id": feedback.user_id,
                "created_at": feedback.created_at.isoformat() if feedback.created_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting feedback detail: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy chi tiết phản hồi: {str(e)}"
        )
