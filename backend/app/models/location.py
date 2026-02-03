from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime

class RecyclingLocation(Base):
    """
    Model for recycling collection points
    """
    __tablename__ = "recycling_locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    address = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    waste_types = Column(String(200))  # Comma-separated types: "battery, electronics, paper"
    operating_hours = Column(String(100))
    contact_phone = Column(String(20))
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<RecyclingLocation(id={self.id}, name={self.name}, city='TP.HCM')>"
