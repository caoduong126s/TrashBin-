from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.location import RecyclingLocation

router = APIRouter()

# --- Schemas ---
class LocationBase(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    waste_types: str
    operating_hours: Optional[str] = None
    contact_phone: Optional[str] = None
    description: Optional[str] = None

class LocationResponse(LocationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Endpoints ---

@router.get("/", response_model=List[LocationResponse])
async def get_locations(
    waste_type: Optional[str] = Query(None, description="Filter by waste type (e.g. 'battery')"),
    db: Session = Depends(get_db)
):
    """
    Get all recycling locations, optionally filtered by waste type
    """
    query = db.query(RecyclingLocation)
    
    if waste_type:
        query = query.filter(RecyclingLocation.waste_types.contains(waste_type.lower()))
    
    return query.all()

@router.post("/seed", status_code=201)
async def seed_tphcm_locations(db: Session = Depends(get_db)):
    """
    Seed initial recycling locations for TP.HCM
    Reference: 'Việt Nam Tái Chế' program and local collection points
    """
    # Check if data already exists
    if db.query(RecyclingLocation).count() > 0:
        return {"message": "Locations already seeded"}

    locations = [
        {
            "name": "UBND Phường Đa Kao (Điểm thu gom Pin)",
            "address": "58-60 Nguyễn Văn Thủ, Đa Kao, Quận 1, TP.HCM",
            "latitude": 10.7877,
            "longitude": 106.6983,
            "waste_types": "pin, rác điện tử",
            "operating_hours": "08:00 - 17:00 (Thứ 2 - Thứ 6)",
            "description": "Điểm thu gom pin cũ và thiết bị điện tử nhỏ thuộc chương trình Việt Nam Tái Chế."
        },
        {
            "name": "MM Mega Market An Phú",
            "address": "Khu đô thị mới An Phú, An Khánh, Quận 2, TP.HCM",
            "latitude": 10.7935,
            "longitude": 106.7410,
            "waste_types": "pin, rác điện tử, nhựa, giấy",
            "operating_hours": "06:00 - 22:00 (Hàng ngày)",
            "description": "Trạm thu gom đa loại rác tái chế đặt tại cổng siêu thị MM Mega Market."
        },
        {
            "name": "UBND Phường 15, Quận 4",
            "address": "132 Tôn Thất Thuyết, Phường 15, Quận 4, TP.HCM",
            "latitude": 10.7562,
            "longitude": 106.7118,
            "waste_types": "pin, rác điện tử",
            "operating_hours": "07:30 - 16:30 (Thứ 2 - Thứ 6)",
            "description": "Điểm tiếp nhận rác thải nguy hại hộ gia đình."
        },
        {
            "name": "Siêu thị Co.op Mart Rạch Miễu",
            "address": "48 Hoa Sứ, Phường 7, Phú Nhuận, TP.HCM",
            "latitude": 10.7961,
            "longitude": 106.6885,
            "waste_types": "pin, rác điện tử",
            "operating_hours": "07:30 - 22:00 (Hàng ngày)",
            "description": "Thùng thu gom pin đặt tại khu vực dịch vụ khách hàng."
        },
        {
            "name": "UBND Phường 9, Quận 3",
            "address": "82 Bà Huyện Thanh Quan, Phường 9, Quận 3, TP.HCM",
            "latitude": 10.7795,
            "longitude": 106.6792,
            "waste_types": "pin, rác điện tử",
            "description": "Trạm thu gom thiết bị điện tử cũ hư hỏng."
        }
    ]

    for loc_data in locations:
        loc = RecyclingLocation(**loc_data)
        db.add(loc)
    
    db.commit()
    return {"message": f"Successfully seeded {len(locations)} locations in TP.HCM"}
