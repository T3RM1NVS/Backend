from sqlalchemy import Column, Integer, BigInteger, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()
def now(): return datetime.datetime.utcnow()

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    name = Column(String)
    phone = Column(String)
    created_at = Column(DateTime, default=now)

class ParkingLot(Base):
    __tablename__ = "parking_lots"
    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    total_slots = Column(Integer, default=0)
    created_at = Column(DateTime, default=now)
    slots = relationship("Slot", back_populates="lot", cascade="all, delete-orphan")

class Slot(Base):
    __tablename__ = "slots"
    id = Column(BigInteger, primary_key=True)
    lot_id = Column(BigInteger, ForeignKey("parking_lots.id", ondelete="CASCADE"), nullable=False)
    slot_code = Column(String)
    slot_type = Column(String)
    status = Column(String, default="free")  # free, reserved, occupied
    current_booking_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=now)
    lot = relationship("ParkingLot", back_populates="slots")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    slot_id = Column(BigInteger, ForeignKey("slots.id", ondelete="CASCADE"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, default="pending")  # pending, active, expired
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now)
