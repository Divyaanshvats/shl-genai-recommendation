"""
Pydantic schemas for FastAPI request/response
"""

from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class RecommendRequest(BaseModel):
    query: str

class RecommendedAssessment(BaseModel):
    url: str
    name: str
    adaptive_support: str
    description: str
    duration: int
    remote_support: str
    test_type: List[str]

class RecommendResponse(BaseModel):
    recommended_assessments: List[RecommendedAssessment]

class HealthResponse(BaseModel):
    status: str
