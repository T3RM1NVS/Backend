from fastapi import FastAPI
from database import init_db
from tasks import start_scheduler
import users, parking, bookings
from ml_api import router as ml_router

app = FastAPI(title="Async Parking Backend")

app.include_router(users.router)
app.include_router(parking.router)
app.include_router(bookings.router)
app.include_router(ml_router)

@app.on_event("startup")
async def on_startup():
    await init_db()
    start_scheduler()
    print("App started with DB initialized and APScheduler running.")

@app.get("/")
async def root():
    return {"message": "Parking Backend Running"}
