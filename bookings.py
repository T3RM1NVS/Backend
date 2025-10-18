from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models import Booking, Slot
from database import AsyncSessionLocal
from schemas import BookingCreate, BookingRead
from typing import List
from datetime import datetime

router = APIRouter(prefix="/bookings", tags=["bookings"])

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=BookingRead)
async def create_booking(booking: BookingCreate, session: AsyncSession = Depends(get_session)):
    # Check if slot exists
    result = await session.execute(select(Slot).where(Slot.id == booking.slot_id))
    slot = result.scalar_one_or_none()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")

    # Check if slot is free
    if slot.status != "free":
        raise HTTPException(status_code=400, detail="Slot not available")

    # Check for overlapping bookings for the same slot
    overlapping = await session.execute(
        select(Booking).where(
            and_(
                Booking.slot_id == booking.slot_id,
                Booking.status == "active",
                Booking.start_time < booking.end_time,
                Booking.end_time > booking.start_time
            )
        )
    )
    if overlapping.scalars().first():
        raise HTTPException(status_code=400, detail="Slot already booked for the given time range")

    # Create new booking
    new_booking = Booking(
        user_id=booking.user_id,
        slot_id=booking.slot_id,
        start_time=booking.start_time,
        end_time=booking.end_time,
        status="active"
    )

    # Update slot status
    slot.status = "reserved"
    slot.current_booking_id = None  # will be set after booking is persisted

    session.add(new_booking)
    await session.commit()
    await session.refresh(new_booking)

    # Now update slot.current_booking_id with the booking id
    slot.current_booking_id = new_booking.id
    session.add(slot)
    await session.commit()

    return new_booking

@router.get("/", response_model=List[BookingRead])
async def list_bookings(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Booking))
    return result.scalars().all()
