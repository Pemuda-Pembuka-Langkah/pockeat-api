"""
Models for exercise analysis.
"""

import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class ExerciseAnalysisResult(BaseModel):
    """Exercise analysis result model."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Unique identifier"
    )
    exercise_type: str = Field(description="Type of exercise (e.g., cardio, strength)")
    calories_burned: float = Field(description="Estimated calories burned")
    duration: str = Field(description="Duration in minutes")
    intensity: str = Field(description="Exercise intensity (low, medium, high)")
    met_value: float = Field(description="MET value for the exercise")
    error: Optional[str] = Field(
        default=None, description="Error message if analysis failed"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Timestamp of analysis"
    )


class ExerciseAnalysisRequest(BaseModel):
    """Exercise analysis request model."""

    description: str = Field(description="Description of the exercise to analyze")
    user_weight_kg: Optional[float] = Field(
        default=None, description="User's weight in kilograms"
    )
    user_height_cm: Optional[float] = Field(
        default=None, description="User's height in centimeters"
    )
    user_age: Optional[int] = Field(
        default=None, description="User's age in years"
    )
    user_gender: Optional[str] = Field(
        default=None, description="User's gender (male/female)"
    )


class ExerciseCorrectionRequest(BaseModel):
    """Exercise correction request model."""
    
    previous_result: ExerciseAnalysisResult = Field(
        description="Previous analysis result to correct"
    )
    user_comment: Optional[str] = Field(
        description="User's feedback for correction"
    )
    user_weight_kg: Optional[float] = Field(
        default=None, description="User's weight in kilograms"
    )
    user_height_cm: Optional[float] = Field(
        default=None, description="User's height in centimeters"
    )
    user_age: Optional[int] = Field(
        default=None, description="User's age in years"
    )
    user_gender: Optional[str] = Field(
        default=None, description="User's gender (male/female)"
    )
