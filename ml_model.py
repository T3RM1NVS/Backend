import joblib
import pandas as pd
from math import radians, sin, cos, sqrt, atan2
from pathlib import Path

# ============================================================
# Load trained model (RandomForestRegressor pipeline)
# ============================================================
MODEL_PATH = Path(__file__).parent / "parking_availability_model.joblib"
model = joblib.load(MODEL_PATH)

# ============================================================
# Load or mock parking data
# ============================================================
DATA_PATH = Path(__file__).parent / "parking_locations.csv"

if DATA_PATH.exists():
    parking_df = pd.read_csv(DATA_PATH)
else:
    # fallback demo data (so app still works)
    parking_df = pd.DataFrame([
        {"lat": 12.9716, "lon": 77.5946, "osm_type": "surface"},
        {"lat": 12.975, "lon": 77.598, "osm_type": "underground"},
        {"lat": 12.968, "lon": 77.590, "osm_type": "multi-level"},
    ])

# ============================================================
# Utility: Haversine distance calculator
# ============================================================
def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance between two coordinates (km)."""
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# ============================================================
# Core function: Get top 3 nearest parkings
# ============================================================
def get_top3_nearest_parkings(dest_lat: float, dest_lon: float):
    """Return 3 nearest parkings with model-predicted availability."""
    df = parking_df.copy()

    # Compute distances
    df["distance_km"] = df.apply(
        lambda row: haversine_distance(dest_lat, dest_lon, row["lat"], row["lon"]),
        axis=1,
    )

    # Predict availability
    try:
        df["predicted_availability"] = model.predict(df[["lat", "lon", "osm_type"]])
    except Exception as e:
        raise RuntimeError(f"Prediction failed: {e}")

    # Sort by distance
    nearest = df.sort_values("distance_km").head(3)
    return nearest[
        ["lat", "lon", "osm_type", "predicted_availability", "distance_km"]
    ].to_dict(orient="records")
