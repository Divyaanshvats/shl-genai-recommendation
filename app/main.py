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

# Include routes
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    print("Starting up SHL Recommender API...")
    from app.routes import get_engine
    # Pre-initialize engine at startup to avoid first-request timeout
    try:
        get_engine()
        print("Recommendation engine initialized successfully.")
    except Exception as e:
        print(f"Error during engine initialization: {e}")

@app.get("/")
async def root():
    return {"message": "SHL Recommender API is running", "endpoints": ["/health", "/recommend"]}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
