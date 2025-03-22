from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ExerciseAnalysisResult(BaseModel):
    """
    Exercise analysis result containing exercise type, duration, intensity,
    calories burned, and MET value.
    """
    exercise_type: str
    duration: str
    intensity: str
    estimated_calories: int = Field(ge=0)
    met_value: float = Field(ge=0)
    summary: str
    timestamp: datetime = Field(default_factory=datetime.now)
    original_input: str
    missing_info: List[str] = []
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 