from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base

class CrowdsourcedImage(Base):
    """Model for user-submitted images to expand dataset"""
    __tablename__ = "crowdsourced_images"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String(500), nullable=False)
    user_label = Column(String(50), nullable=False, index=True)  # User's classification
    user_id = Column(String(100), index=True, default="anonymous")
    verified = Column(Boolean, default=False, index=True)  # Admin verified
    admin_comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now, server_default=func.now())

    def __repr__(self):
        return f"<CrowdsourcedImage(id={self.id}, label={self.user_label}, verified={self.verified})>"
