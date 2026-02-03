from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

from datetime import datetime

class ClassificationHistory(Base):
    __tablename__ = "classification_history"

    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(50), index=True)
    class_name_vn = Column(String(50))
    confidence = Column(Float)
    bin_type = Column(String(20), index=True)
    processing_time = Column(Float)
    user_id = Column(String(100), index=True)  # "anonymous" or user identifier
    created_at = Column(DateTime(timezone=True), default=datetime.now, server_default=func.now())
    
    # Optional: Box coordinates if needed later
    # box_x1 = Column(Integer, nullable=True)
    # box_y1 = Column(Integer, nullable=True)
    # box_x2 = Column(Integer, nullable=True)
    # box_y2 = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<ClassificationHistory(id={self.id}, class={self.class_name}, bin={self.bin_type})>"
