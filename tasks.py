import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from sqlalchemy import select, update
from database import AsyncSessionLocal
from models import Booking, Slot

async def cleanup_expired_bookings():
    async with AsyncSessionLocal() as session:
        now = datetime.utcnow()
        result = await session.execute(
            select(Booking).where(Booking.end_time < now, Booking.status == "active")
        )
        expired_bookings = result.scalars().all()
        for booking in expired_bookings:
            booking.status = "expired"
            slot = await session.get(Slot, booking.slot_id)
            if slot:
                slot.status = "free"
                slot.current_booking_id = None
        await session.commit()
        print(f"{len(expired_bookings)} expired bookings cleaned up.")

def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(cleanup_expired_bookings, "interval", minutes=1)
    scheduler.start()
