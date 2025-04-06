"""
Main service for Gemini API integration.
"""

import os
from typing import Optional

from api.services.gemini.exceptions import GeminiServiceException, GeminiAPIKeyMissingError
from api.services.gemini.food_service import FoodAnalysisService
from api.services.gemini.exercise_service import ExerciseAnalysisService
from api.models.food_analysis import FoodAnalysisResult
from api.models.exercise_analysis import ExerciseAnalysisResult


class GeminiService:
    """Main service for Gemini API integration.

    This class follows the Single Responsibility Principle by delegating
    specialized tasks to dedicated service classes:
    - FoodAnalysisService for food-related analysis
    - ExerciseAnalysisService for exercise-related analysis
    """

    def __init__(self):
        """Initialize the Gemini service.

        Raises:
            GeminiAPIKeyMissingError: If the Gemini API key is not set.
        """
        # Check if API key is set
        if not os.getenv("GOOGLE_API_KEY"):
            raise GeminiAPIKeyMissingError()

        # Initialize specialized services
        self.food_service = FoodAnalysisService()
        self.exercise_service = ExerciseAnalysisService()

    async def check_health(self) -> bool:
        """Check if the Gemini service is healthy.

        Returns:
            True if the service is healthy, False otherwise.
        """
        # Basic check that just ensures API key is set
        return os.getenv("GOOGLE_API_KEY") is not None

    # Food analysis methods

    async def analyze_food_by_text(self, description: str) -> FoodAnalysisResult:
        """Analyze food from a text description.

        Args:
            description: The food description.

        Returns:
            The food analysis result.

        Raises:
            GeminiServiceException: If the analysis fails.
        """
        return await self.food_service.analyze_by_text(description)

    async def analyze_food_by_image(self, image_file) -> FoodAnalysisResult:
        """Analyze food from an image.

        Args:
            image_file: The image file (file-like object).

        Returns:
            The food analysis result.

        Raises:
            GeminiServiceException: If the analysis fails.
        """
        return await self.food_service.analyze_by_image(image_file)

    async def analyze_nutrition_label(
        self, image_file, servings: float = 1.0
    ) -> FoodAnalysisResult:
        """Analyze a nutrition label image.

        Args:
            image_file: The image file (file-like object).
            servings: The number of servings.

        Returns:
            The food analysis result.

        Raises:
            GeminiServiceException: If the analysis fails.
        """
        return await self.food_service.analyze_nutrition_label(image_file, servings)

    async def correct_food_analysis(
        self, previous_result: FoodAnalysisResult, user_comment: str
    ) -> FoodAnalysisResult:
        """Correct a previous food analysis based on user feedback.

        Args:
            previous_result: The previous food analysis result.
            user_comment: The user's feedback.

        Returns:
            The corrected food analysis result.

        Raises:
            GeminiServiceException: If the correction fails.
        """
        return await self.food_service.correct_analysis(previous_result, user_comment)

    # Exercise analysis methods

    async def analyze_exercise(
        self, description: str, user_weight_kg: Optional[float] = None
    ) -> ExerciseAnalysisResult:
        """Analyze an exercise description.

        Args:
            description: The exercise description.
            user_weight_kg: The user's weight in kilograms.

        Returns:
            The exercise analysis result.

        Raises:
            GeminiServiceException: If the analysis fails.
        """
        return await self.exercise_service.analyze(description, user_weight_kg)

    async def correct_exercise_analysis(
        self, previous_result: ExerciseAnalysisResult, user_comment: str
    ) -> ExerciseAnalysisResult:
        """Correct a previous exercise analysis based on user feedback.

        Args:
            previous_result: The previous exercise analysis result.
            user_comment: The user's feedback.

        Returns:
            The corrected exercise analysis result.

        Raises:
            GeminiServiceException: If the correction fails.
        """
        return await self.exercise_service.correct_analysis(previous_result, user_comment)
