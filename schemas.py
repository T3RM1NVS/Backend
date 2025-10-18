from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str]
    phone: Optional[str]

class UserRead(BaseModel):
    id: int
    email: str
    name: Optional[str]
    phone: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class BookingCreate(BaseModel):
    user_id: int
    slot_id: int
    start_time: datetime
    end_time: datetime

class BookingRead(BaseModel):
    id: int
    user_id: int
    slot_id: int
    start_time: datetime
    end_time: datetime
    status: str

    class Config:
        orm_mode = True

class SlotRead(BaseModel):
    id: int
    lot_id: int
    slot_code: str
    slot_type: str
    status: str
    current_booking_id: Optional[int]

    class Config:
        orm_mode = True

class ParkingLotRead(BaseModel):
    id: int
    name: str
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    total_slots: int

    class Config:
        orm_mode = True
