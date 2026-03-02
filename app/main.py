"""
FastAPI Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
import uvicorn

app = FastAPI(title="SHL Candidate Recommendation API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
# Limit PyTorch threads to reduce memory footprint on Render free tier
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

# Include routes
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "SHL Recommender API is running", "endpoints": ["/health", "/recommend"]}

if __name__ == "__main__":
    # Increase timeout limits to allow heavy ML model to load on Render free tier
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        timeout_keep_alive=120,
        workers=1,
        limit_concurrency=10,
        reload=False  # Disable reload in production to save memory
    )

