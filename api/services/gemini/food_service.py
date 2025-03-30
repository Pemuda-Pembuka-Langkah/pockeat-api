"""
Food analysis service using Gemini API.

This module is kept for backwards compatibility.
New code should use the api.services.gemini.food.FoodAnalysisServiceFactory class instead.
"""

import logging

from api.services.gemini.food.service_factory import FoodAnalysisServiceFactory
from api.models.food_analysis import FoodAnalysisResult

# Configure logger
logger = logging.getLogger(__name__)


class FoodAnalysisService:
    """
    Food analysis service using Gemini API.
    
    This class is kept for backwards compatibility.
    New code should use the api.services.gemini.food.FoodAnalysisServiceFactory class instead.
    """
    
    def __init__(self):
        """Initialize the service."""
        self._factory = FoodAnalysisServiceFactory()
        logger.info("Initializing FoodAnalysisService (legacy wrapper)")
    
    async def analyze_by_text(self, description: str) -> FoodAnalysisResult:
        """Analyze food from a text description."""
        return await self._factory.analyze_by_text(description)
    
    async def analyze_by_image(self, image_file) -> FoodAnalysisResult:
        """Analyze food from an image."""
        return await self._factory.analyze_by_image(image_file)
    
    async def analyze_nutrition_label(self, image_file, servings: float = 1.0) -> FoodAnalysisResult:
        """Analyze a nutrition label image."""
        return await self._factory.analyze_nutrition_label(image_file, servings)
    
    async def correct_analysis(self, previous_result: FoodAnalysisResult, user_comment: str) -> FoodAnalysisResult:
        """Correct a previous food analysis based on user feedback."""
        return await self._factory.correct_analysis(previous_result, user_comment)
    
    async def correct_nutrition_label(self, previous_result: FoodAnalysisResult, user_comment: str, servings: float = 1.0) -> FoodAnalysisResult:
        """Correct a previous nutrition label analysis based on user feedback."""
        return await self._factory.correct_nutrition_label(previous_result, user_comment, servings) 