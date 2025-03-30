"""
Food analysis service factory.
"""

import logging
from typing import Dict, Any, Optional

from api.models.food_analysis import FoodAnalysisResult
from api.services.gemini.food.text_analysis_service import FoodTextAnalysisService
from api.services.gemini.food.image_analysis_service import FoodImageAnalysisService
from api.services.gemini.food.nutrition_label_service import NutritionLabelAnalysisService
from api.services.gemini.food.correction_service import FoodCorrectionService

# Configure logger
logger = logging.getLogger(__name__)


class FoodAnalysisServiceFactory:
    """Factory for food analysis services."""
    
    def __init__(self):
        """Initialize the factory."""
        self.text_service = FoodTextAnalysisService()
        self.image_service = FoodImageAnalysisService()
        self.nutrition_label_service = NutritionLabelAnalysisService()
        self.correction_service = FoodCorrectionService()
        logger.info("Initialized FoodAnalysisServiceFactory")
    
    async def analyze_by_text(self, description: str) -> FoodAnalysisResult:
        """Analyze food from a text description.
        
        Args:
            description: The food description.
            
        Returns:
            The food analysis result.
        """
        return await self.text_service.analyze(description)
    
    async def analyze_by_image(self, image_file) -> FoodAnalysisResult:
        """Analyze food from an image.
        
        Args:
            image_file: The image file (file-like object).
            
        Returns:
            The food analysis result.
        """
        return await self.image_service.analyze(image_file)
    
    async def analyze_nutrition_label(self, image_file, servings: float = 1.0) -> FoodAnalysisResult:
        """Analyze a nutrition label image.
        
        Args:
            image_file: The image file (file-like object).
            servings: The number of servings.
            
        Returns:
            The food analysis result.
        """
        return await self.nutrition_label_service.analyze(image_file, servings)
    
    async def correct_analysis(self, previous_result: FoodAnalysisResult, user_comment: str) -> FoodAnalysisResult:
        """Correct a previous food analysis based on user feedback.
        
        Args:
            previous_result: The previous food analysis result.
            user_comment: The user's feedback.
            
        Returns:
            The corrected food analysis result.
        """
        return await self.correction_service.correct_food_analysis(previous_result, user_comment)
    
    async def correct_nutrition_label(self, previous_result: FoodAnalysisResult, user_comment: str, servings: float = 1.0) -> FoodAnalysisResult:
        """Correct a previous nutrition label analysis based on user feedback.
        
        Args:
            previous_result: The previous food analysis result.
            user_comment: The user's feedback.
            servings: The number of servings.
            
        Returns:
            The corrected food analysis result.
        """
        return await self.correction_service.correct_nutrition_label(previous_result, user_comment, servings) 