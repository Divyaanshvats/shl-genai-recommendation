"""
FastAPI Routes
"""

from fastapi import APIRouter, HTTPException
from app.schemas import RecommendRequest, RecommendResponse, HealthResponse
from recommender.engine import RecommendationEngine

router = APIRouter()
engine = None

def get_engine():
    global engine
    if engine is None:
        engine = RecommendationEngine()
    return engine

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return {"status": "healthy"}

@router.post("/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest):
    try:
        recommender = get_engine()
        results = recommender.get_recommendations(request.query)
        
        # Ensure results match schema
        formatted_results = []
        for r in results:
            formatted_results.append({
                "url": r.get("url"),
                "name": r.get("name"),
                "adaptive_support": r.get("adaptive_support", "No"),
                "description": r.get("description", ""),
                "duration": int(r.get("duration", 30)),
                "remote_support": r.get("remote_support", "No"),
                "test_type": r.get("test_type", [])
            })
            
        return {"recommended_assessments": formatted_results}
    except Exception as e:
        print(f"Error in recommend endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
