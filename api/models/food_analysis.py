"""
Food analysis models using Pydantic for FastAPI.
"""

from datetime import datetime
from typing import List, Optional
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
    sodium: float = Field(default=0, description="Sodium in milligrams")
    fiber: float = Field(default=0, description="Fiber in grams")
    sugar: float = Field(default=0, description="Sugar in grams")
    

class FoodAnalysisResult(BaseModel):
    """Food analysis result model."""
    
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier")
    food_name: str = Field(description="Name of the food")
    ingredients: List[Ingredient] = Field(default_factory=list, description="List of ingredients")
    nutrition_info: NutritionInfo = Field(default_factory=NutritionInfo, description="Nutrition information")
    error: Optional[str] = Field(default=None, description="Error message if analysis failed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of analysis")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "food_name": "Grilled Chicken Salad",
                "ingredients": [
                    {"name": "Chicken Breast", "servings": 100},
                    {"name": "Lettuce", "servings": 50},
                    {"name": "Tomato", "servings": 25}
                ],
                "nutrition_info": {
                    "calories": 250,
                    "protein": 30,
                    "carbs": 15,
                    "fat": 10,
                    "sodium": 300,
                    "fiber": 3,
                    "sugar": 5
                },
                "timestamp": "2023-03-25T12:00:00Z"
            }
        }


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
    
    previous_result: FoodAnalysisResult = Field(description="Previous analysis result to correct")
    user_comment: str = Field(description="User's feedback for correction")
    servings: Optional[float] = Field(default=1.0, description="Number of servings")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "previous_result": {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "food_name": "Grilled Chiken Salad", # Misspelled intentionally for example
                    "ingredients": [
                        {"name": "Chicken Breast", "servings": 100},
                        {"name": "Lettuce", "servings": 50},
                        {"name": "Tomato", "servings": 25}
                    ],
                    "nutrition_info": {
                        "calories": 250,
                        "protein": 30,
                        "carbs": 15,
                        "fat": 10,
                        "sodium": 300,
                        "fiber": 3,
                        "sugar": 5
                    },
                    "timestamp": "2023-03-25T12:00:00Z"
                },
                "user_comment": "The name should be 'Grilled Chicken Salad', not 'Grilled Chiken Salad'",
                "servings": 1.0
            }
        } 