from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models import ParkingLot, Slot
from database import AsyncSessionLocal
from schemas import ParkingLotRead, SlotRead
from typing import List

router = APIRouter(prefix="/parking", tags=["parking"])

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/lots", response_model=List[ParkingLotRead])
async def list_parking_lots(session: AsyncSession = Depends(get_session)):
    result = await session.execute(ParkingLot.__table__.select())
    return result.scalars().all()

@router.get("/slots", response_model=List[SlotRead])
async def list_slots(session: AsyncSession = Depends(get_session)):
    result = await session.execute(Slot.__table__.select())
    return result.scalars().all()
