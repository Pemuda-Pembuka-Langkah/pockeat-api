"""
Exercise analysis API data models.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ExerciseAnalysisRequest(BaseModel):
    """Request model for exercise analysis."""
    description: str = Field(..., description="Description of the exercise performed")


class ExerciseAnalysisResponse(BaseModel):
    """Response model for exercise analysis."""
    exercise: str
    calories_burned: float
    duration_minutes: Optional[int] = None
    intensity: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None


class ExerciseCorrectionRequest(BaseModel):
    """Request model for exercise correction."""
    exercise_entry: str = Field(..., description="The original exercise entry")
    user_correction: str = Field(..., description="User's correction or additional information")


class ExerciseCorrectionResponse(BaseModel):
    """Response model for exercise correction."""
    exercise: str
    calories_burned: float
    duration_minutes: Optional[int] = None
    intensity: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None 