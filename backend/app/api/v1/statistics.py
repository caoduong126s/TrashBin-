"""
Statistics API Endpoints
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.statistics import statistics_service

router = APIRouter(tags=["statistics"])


@router.get("/dashboard")
async def get_dashboard_statistics(
    period: str = Query("week", pattern="^(today|week|month)$"),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics
    
    Query params:
        period: "today", "week", or "month"
        
    Returns:
        Complete dashboard statistics
    """
    try:
        stats = statistics_service.get_dashboard_stats(db, period)
        
        return {
            "success": True,
            "data": stats,
            "period": period
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/summary")
async def get_summary_stats(
    days: Optional[int] = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics
    
    Query params:
        days: Number of days to include (default: 7)
        
    Returns:
        Summary statistics
    """
    try:
        total = statistics_service.get_total_classifications(db, days)
        recyclable = statistics_service.get_recyclable_count(db, days)
        accuracy = statistics_service.get_accuracy_rate(db, days)
        co2_saved = statistics_service.get_co2_saved(db, days)
        
        return {
            "success": True,
            "data": {
                "total_classifications": total,
                "recyclable_count": recyclable,
                "accuracy_rate": round(accuracy, 1),
                "co2_saved_kg": co2_saved,
                "period_days": days
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/trend")
async def get_trend(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get classification trend"""
    try:
        trend_data = statistics_service.get_trend_data(db, days)
        
        return {
            "success": True,
            "data": trend_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/distribution/bins")
async def get_bin_distribution(
    days: Optional[int] = Query(None, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get distribution by bin type"""
    try:
        distribution = statistics_service.get_bin_distribution(db, days)
        
        return {
            "success": True,
            "data": distribution
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/distribution/classes")
async def get_class_distribution(
    days: Optional[int] = Query(None, ge=1, le=365),
    top_n: int = Query(4, ge=1, le=9),
    db: Session = Depends(get_db)
):
    """Get distribution by waste class"""
    try:
        distribution = statistics_service.get_class_distribution(db, days, top_n)
        
        return {
            "success": True,
            "data": distribution
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }