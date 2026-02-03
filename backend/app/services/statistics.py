"""
Statistics Service

Handles statistical analysis of classification history
"""

from sqlalchemy import func, extract
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, List
from collections import Counter

from app.models.classification import ClassificationHistory


class StatisticsService:
    """Service for generating statistics"""
    
    @staticmethod
    def get_total_classifications(db: Session, days: int = None) -> int:
        """Get total number of classifications"""
        query = db.query(func.count(ClassificationHistory.id))
        
        if days:
            start_date = datetime.now() - timedelta(days=days)
            query = query.filter(ClassificationHistory.created_at >= start_date)
        
        return query.scalar() or 0
    
    @staticmethod
    def get_recyclable_count(db: Session, days: int = None) -> int:
        """Get count of recyclable items"""
        query = db.query(func.count(ClassificationHistory.id)).filter(
            ClassificationHistory.bin_type == "recyclable"
        )
        
        if days:
            start_date = datetime.now() - timedelta(days=days)
            query = query.filter(ClassificationHistory.created_at >= start_date)
        
        return query.scalar() or 0
    
    @staticmethod
    def get_accuracy_rate(db: Session, days: int = None) -> float:
        """Get average confidence (proxy for accuracy)"""
        query = db.query(func.avg(ClassificationHistory.confidence))
        
        if days:
            start_date = datetime.now() - timedelta(days=days)
            query = query.filter(ClassificationHistory.created_at >= start_date)
        
        result = query.scalar()
        return float(result) if result else 0.0
    
    @staticmethod
    def get_co2_saved(db: Session, days: int = None) -> float:
        """
        Calculate CO2 saved (estimate)
        Assumption: 1kg of recycled waste saves ~0.5kg CO2
        Average waste weight: ~0.5kg per item
        """
        recyclable_count = StatisticsService.get_recyclable_count(db, days)
        # Estimate: 0.5kg per item * 0.5kg CO2 saved per kg = 0.25kg CO2 per item
        co2_saved = recyclable_count * 0.25
        return round(co2_saved, 1)
    
    @staticmethod
    def get_trend_data(db: Session, days: int = 7) -> List[Dict]:
        """
        Get classification trend for the last N days
        Returns: [{"date": "T2", "count": 45}, ...]
        """
        start_date = datetime.now() - timedelta(days=days)
        
        # Group by date
        results = db.query(
            func.date(ClassificationHistory.created_at).label('date'),
            func.count(ClassificationHistory.id).label('count')
        ).filter(
            ClassificationHistory.created_at >= start_date
        ).group_by(
            func.date(ClassificationHistory.created_at)
        ).order_by('date').all()
        
        # Format for frontend
        weekdays = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
        trend_data = []
        
        for result in results:
            date_obj = datetime.strptime(str(result.date), "%Y-%m-%d")
            weekday = weekdays[date_obj.weekday()]
            trend_data.append({
                "date": weekday,
                "count": result.count
            })
        
        return trend_data
    
    @staticmethod
    def get_bin_distribution(db: Session, days: int = None) -> Dict:
        """
        Get distribution by bin type
        Returns: {"recyclable": 1200, "general": 500, "hazardous": 142}
        """
        query = db.query(
            ClassificationHistory.bin_type,
            func.count(ClassificationHistory.id).label('count')
        )
        
        if days:
            start_date = datetime.now() - timedelta(days=days)
            query = query.filter(ClassificationHistory.created_at >= start_date)
        
        results = query.group_by(ClassificationHistory.bin_type).all()
        
        distribution = {
            "recyclable": 0,
            "general": 0,
            "hazardous": 0,
            "organic": 0
        }
        
        for result in results:
            if result.bin_type in distribution:
                distribution[result.bin_type] = result.count
        
        return distribution
    
    @staticmethod
    def get_class_distribution(db: Session, days: int = None, top_n: int = 4) -> Dict:
        """
        Get distribution by waste class
        Returns: {"plastic": 850, "paper": 620, ...}
        """
        query = db.query(
            ClassificationHistory.class_name_vn,
            func.count(ClassificationHistory.id).label('count')
        )
        
        if days:
            start_date = datetime.now() - timedelta(days=days)
            query = query.filter(ClassificationHistory.created_at >= start_date)
        
        results = query.group_by(
            ClassificationHistory.class_name_vn
        ).order_by(
            func.count(ClassificationHistory.id).desc()
        ).limit(top_n).all()
        
        distribution = {}
        for result in results:
            distribution[result.class_name_vn] = result.count
        
        return distribution
    
    @staticmethod
    def get_dashboard_stats(db: Session, period: str = "week") -> Dict:
        """
        Get all statistics for dashboard
        
        Args:
            period: "today", "week", "month"
        """
        days_map = {
            "today": 1,
            "week": 7,
            "month": 30
        }
        days = days_map.get(period, 7)
        
        # Get previous period for comparison
        prev_days = days * 2
        
        # Current period stats
        total_current = StatisticsService.get_total_classifications(db, days)
        recyclable_current = StatisticsService.get_recyclable_count(db, days)
        accuracy_current = StatisticsService.get_accuracy_rate(db, days)
        co2_current = StatisticsService.get_co2_saved(db, days)
        
        # Previous period stats (for comparison)
        total_prev = StatisticsService.get_total_classifications(db, prev_days) - total_current
        recyclable_prev = StatisticsService.get_recyclable_count(db, prev_days) - recyclable_current
        accuracy_prev = StatisticsService.get_accuracy_rate(db, prev_days)
        co2_prev = recyclable_prev * 0.25
        
        # Calculate percentage changes
        def calc_change(current, previous):
            if previous == 0:
                return 100.0 if current > 0 else 0.0
            return round(((current - previous) / previous) * 100, 1)
        
        return {
            "summary": {
                "total": {
                    "value": total_current,
                    "change": calc_change(total_current, total_prev)
                },
                "recyclable": {
                    "value": recyclable_current,
                    "change": calc_change(recyclable_current, recyclable_prev)
                },
                "accuracy": {
                    "value": round(accuracy_current, 1),
                    "change": calc_change(accuracy_current, accuracy_prev)
                },
                "co2_saved": {
                    "value": co2_current,
                    "change": calc_change(co2_current, co2_prev)
                }
            },
            "trend": StatisticsService.get_trend_data(db, days),
            "bin_distribution": StatisticsService.get_bin_distribution(db, days),
            "class_distribution": StatisticsService.get_class_distribution(db, days)
        }


# Global instance
statistics_service = StatisticsService()