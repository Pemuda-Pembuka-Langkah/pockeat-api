"""
Models package for the API.
"""

from api.models.food_analysis import (
    Ingredient,
    NutritionInfo,
    FoodAnalysisResult,
    FoodAnalysisRequest,
    FoodCorrectionRequest,
)

from api.models.exercise_analysis import (
    ExerciseAnalysisResult,
    ExerciseAnalysisRequest,
    ExerciseCorrectionRequest,
)

__all__ = [
    "Ingredient",
    "NutritionInfo",
    "FoodAnalysisResult",
    "FoodAnalysisRequest",
    "FoodCorrectionRequest",
    "ExerciseAnalysisResult",
    "ExerciseAnalysisRequest",
    "ExerciseCorrectionRequest",
]
