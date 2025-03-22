from pydantic import BaseModel, Field
from typing import List, Optional


class NutritionInfo(BaseModel):
    """Nutrition information model."""
    calories: int = Field(ge=0)
    protein: float = Field(ge=0)
    carbs: float = Field(ge=0)
    fat: float = Field(ge=0)
    sodium: float = Field(ge=0)
    fiber: float = Field(ge=0)
    sugar: float = Field(ge=0)


class Ingredient(BaseModel):
    """Ingredient model with name and serving size."""
    name: str
    servings: float = Field(ge=0)


class FoodAnalysisResult(BaseModel):
    """
    Food analysis result containing nutrition information,
    ingredients, and any relevant warnings.
    """
    food_name: str
    ingredients: List[Ingredient] = []
    nutrition_info: NutritionInfo
    warnings: List[str] = []
    is_low_confidence: Optional[bool] = False 