from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from database import AsyncSessionLocal
from schemas import UserCreate, UserRead
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
router = APIRouter(prefix="/users", tags=["users"])

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=UserRead)
async def create_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    db_user = User(
        email=user.email,
        hashed_password=pwd_context.hash(user.password),
        name=user.name,
        phone=user.phone
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user
