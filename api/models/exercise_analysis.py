"""
Models for exercise analysis.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ExerciseAnalysisResult(BaseModel):
    """Exercise analysis result model."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
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
