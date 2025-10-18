import uvicorn
from main import app
import asyncio

if __name__ == "__main__":
    # Start uvicorn server with asyncio event loop
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
