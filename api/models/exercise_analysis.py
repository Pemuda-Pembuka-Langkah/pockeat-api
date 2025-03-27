"""
Exercise analysis models using Pydantic for FastAPI.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import uuid4
from pydantic import BaseModel, Field, validator


class ExerciseAnalysisResult(BaseModel):
    """Exercise analysis result model."""
    
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier")
    exercise_name: str = Field(description="Name of the exercise")
    exercise_type: str = Field(description="Type of exercise (e.g., cardio, strength)")
    calories_burned: float = Field(description="Estimated calories burned")
    duration_minutes: float = Field(description="Duration in minutes")
    intensity: str = Field(description="Exercise intensity (low, medium, high)")
    muscles_worked: List[str] = Field(default_factory=list, description="List of muscles worked")
    equipment_needed: List[str] = Field(default_factory=list, description="Equipment needed for the exercise")
    benefits: List[str] = Field(default_factory=list, description="Health benefits of the exercise")
    warnings: List[str] = Field(default_factory=list, description="Health warnings for the exercise")
    error: Optional[str] = Field(default=None, description="Error message if analysis failed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of analysis")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "exercise_name": "Running",
                "exercise_type": "cardio",
                "calories_burned": 300,
                "duration_minutes": 30,
                "intensity": "medium",
                "muscles_worked": ["Quadriceps", "Hamstrings", "Calves"],
                "equipment_needed": ["Running shoes"],
                "benefits": ["Improves cardiovascular health", "Burns calories", "Strengthens leg muscles"],
                "warnings": ["High impact on joints"],
                "timestamp": "2023-03-25T12:00:00Z"
            }
        }


class ExerciseAnalysisRequest(BaseModel):
    """Exercise analysis request model."""
    
    description: str = Field(description="Description of the exercise to analyze")
    user_weight_kg: Optional[float] = Field(default=None, description="User's weight in kilograms for calorie calculation")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "description": "30 minute run at 8 km/h pace",
                "user_weight_kg": 70
            }
        }


class ExerciseCorrectionRequest(BaseModel):
    """Exercise correction request model."""
    
    previous_result: ExerciseAnalysisResult = Field(description="Previous analysis result to correct")
    user_comment: str = Field(description="User's feedback for correction")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "previous_result": {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "exercise_name": "Running",
                    "exercise_type": "cardio",
                    "calories_burned": 300,
                    "duration_minutes": 30,
                    "intensity": "medium",
                    "muscles_worked": ["Quadriceps", "Hamstrings", "Calves"],
                    "equipment_needed": ["Running shoes"],
                    "benefits": ["Improves cardiovascular health", "Burns calories", "Strengthens leg muscles"],
                    "warnings": ["High impact on joints"],
                    "timestamp": "2023-03-25T12:00:00Z"
                },
                "user_comment": "I actually ran for 45 minutes, not 30"
            }
        } 