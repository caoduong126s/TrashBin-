from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base

class ClassificationFeedback(Base):
    """Model for user feedback on classification results"""
    __tablename__ = "classification_feedback"

    id = Column(Integer, primary_key=True, index=True)
    classification_id = Column(Integer, ForeignKey("classification_history.id"), nullable=True)
    is_correct = Column(Boolean, nullable=False)
    correct_class = Column(String(50), nullable=True)  # If incorrect, what should it be?
    user_comment = Column(Text, nullable=True)
    user_id = Column(String(100), index=True, default="anonymous")
    created_at = Column(DateTime(timezone=True), default=datetime.now, server_default=func.now())

    def __repr__(self):
        return f"<ClassificationFeedback(id={self.id}, is_correct={self.is_correct})>"
