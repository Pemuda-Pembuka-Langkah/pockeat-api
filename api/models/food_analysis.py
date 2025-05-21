"""
Food analysis models using Pydantic for FastAPI.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    """Ingredient model."""

    name: str
    servings: float = Field(default=0, description="Serving amount in grams")


class NutritionInfo(BaseModel):
    """Nutrition information model."""

    calories: float = Field(default=0, description="Calories in kcal")
    protein: float = Field(default=0, description="Protein in grams")
    carbs: float = Field(default=0, description="Carbohydrates in grams")
    fat: float = Field(default=0, description="Fat in grams")
    saturated_fat: float = Field(default=0, description="Saturated fat in grams")
    sodium: float = Field(default=0, description="Sodium in grams")
    fiber: float = Field(default=0, description="Fiber in grams")
    sugar: float = Field(default=0, description="Sugar in grams")
    cholesterol: float = Field(default=0, description="Cholesterol in mg")
    nutrition_density: float = Field(default=0, description="Nutrition density score (nutrient content per calorie)")
    vitamins_and_minerals: Dict[str, float] = Field(
        default_factory=dict, description="Additional nutrients in appropriate units"
    )


class FoodAnalysisResult(BaseModel):
    """Food analysis result model."""

    id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique identifier"
    )
    food_name: str = Field(description="Name of the food")
    ingredients: List[Ingredient] = Field(
        default_factory=list, description="List of ingredients"
    )
    nutrition_info: Optional[NutritionInfo] = Field(
        default=None, description="Nutrition information"
    )
    health_score: Optional[float] = Field(
        default=None, description="Health score (calculated by Flutter model)"
    )
    warnings: Optional[List[str]] = Field(
        default=None, description="Nutritional warnings (handled by Flutter model)"
    )
    error: Optional[str] = Field(
        default=None, description="Error message if analysis failed"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Timestamp of analysis"
    )



class FoodAnalysisRequest(BaseModel):
    """Food analysis request model for text-based analysis."""

    description: str = Field(description="Description of the food to analyze")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "description": "Grilled chicken breast with a side of mixed vegetables and brown rice"
            }
        }


class FoodCorrectionRequest(BaseModel):
    """Food correction request model."""

    previous_result: FoodAnalysisResult = Field(
        description="Previous analysis result to correct"
    )
    user_comment: str = Field(description="User's feedback for correction")
    servings: Optional[float] = Field(default=1.0, description="Number of servings")