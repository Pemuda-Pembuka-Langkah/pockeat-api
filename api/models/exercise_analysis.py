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
    exercise_type: str = Field(description="Type of exercise (e.g., cardio, strength)")
    calories_burned: float = Field(description="Estimated calories burned")
    duration: str = Field(description="Duration in minutes")
    intensity: str = Field(description="Exercise intensity (low, medium, high)")
    error: Optional[str] = Field(default=None, description="Error message if analysis failed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of analysis")


class ExerciseAnalysisRequest(BaseModel):
    """Exercise analysis request model."""

    description: str = Field(description="Description of the exercise to analyze")
    user_weight_kg: Optional[float] = Field(
        default=None, description="User's weight in kilograms for calorie calculation"
    )


class ExerciseCorrectionRequest(BaseModel):
    """Exercise correction request model."""

    previous_result: ExerciseAnalysisResult = Field(
        description="Previous analysis result to correct"
    )
    user_comment: str = Field(description="User's feedback for correction")
