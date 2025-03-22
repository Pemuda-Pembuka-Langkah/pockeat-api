"""
Food analysis API data models.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class FoodAnalysisResponse(BaseModel):
    """Response model for food analysis."""
    food: str
    calories: float
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbs: Optional[float] = None
    portion_size: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None


class FoodCorrectionRequest(BaseModel):
    """Request model for food correction."""
    food_entry: str = Field(..., description="The original food entry")
    user_correction: str = Field(..., description="User's correction or additional information")


class FoodCorrectionResponse(BaseModel):
    """Response model for food correction."""
    food: str
    calories: float
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbs: Optional[float] = None
    portion_size: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None 