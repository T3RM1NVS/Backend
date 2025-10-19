from fastapi import APIRouter, Query, HTTPException
from ml_model import get_top3_nearest_parkings

router = APIRouter(prefix="/ml", tags=["AI Model"])

@router.get("/recommend")
async def recommend_parking(
    lat: float = Query(..., description="Destination latitude"),
    lon: float = Query(..., description="Destination longitude")
):
    """Predict top 3 nearby parkings and availability."""
    try:
        result = get_top3_nearest_parkings(lat, lon)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
