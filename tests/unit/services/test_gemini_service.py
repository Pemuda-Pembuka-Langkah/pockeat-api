"""
Tests for the GeminiService class.
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Add the project root directory to the Python path so we can import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from api.services.gemini_service import GeminiService
from api.services.gemini.exceptions import GeminiAPIKeyMissingError, GeminiServiceException
from api.models.food_analysis import FoodAnalysisResult, NutritionInfo, Ingredient
from api.models.exercise_analysis import ExerciseAnalysisResult


class TestGeminiService:
    """Test suite for the GeminiService class."""

    @pytest.fixture
    def mock_env(self):
        """Set up environment variables for testing."""
        original_env = os.environ.copy()
        os.environ["GOOGLE_API_KEY"] = "test-api-key"
        yield
        os.environ.clear()
        os.environ.update(original_env)

    @pytest.fixture
    def mock_food_service(self):
        """Create a mock food service."""
        mock = MagicMock()
        mock.analyze_by_text = AsyncMock()
        mock.analyze_by_image = AsyncMock()
        mock.analyze_nutrition_label = AsyncMock()
        mock.correct_analysis = AsyncMock()
        return mock

    @pytest.fixture
    def mock_exercise_service(self):
        """Create a mock exercise service."""
        mock = MagicMock()
        mock.analyze = AsyncMock()
        mock.correct_analysis = AsyncMock()
        return mock

    def test_init_missing_api_key(self):
        """Test initialization with missing API key."""
        with patch.dict(os.environ, clear=True):
            with pytest.raises(GeminiAPIKeyMissingError):
                GeminiService()

    def test_init_with_api_key(self, mock_env):
        """Test successful initialization with API key."""
        with patch('api.services.gemini_service.FoodAnalysisService'), \
             patch('api.services.gemini_service.ExerciseAnalysisService'):
            service = GeminiService()
            assert service is not None
            assert service.food_service is not None
            assert service.exercise_service is not None

    @pytest.mark.asyncio
    async def test_check_health(self, mock_env):
        """Test health check functionality."""
        with patch('api.services.gemini_service.FoodAnalysisService'), \
             patch('api.services.gemini_service.ExerciseAnalysisService'):
            service = GeminiService()
            result = await service.check_health()
            assert result is True

    @pytest.mark.asyncio
    async def test_check_health_api_key_missing(self):
        """Test health check with missing API key."""
        with patch.dict(os.environ, clear=True), \
             patch('api.services.gemini_service.FoodAnalysisService'), \
             patch('api.services.gemini_service.ExerciseAnalysisService'):
            # Manually create a service object without going through __init__
            service = object.__new__(GeminiService)
            # Set required attributes
            service.food_service = MagicMock()
            service.exercise_service = MagicMock()
            
            result = await service.check_health()
            assert result is False

    # Food analysis tests

    @pytest.mark.asyncio
    async def test_analyze_food_by_text(self, mock_env, mock_food_service):
        """Test analyzing food by text description."""
        expected_result = FoodAnalysisResult(
            food_name="Grilled Chicken Salad",
            ingredients=[Ingredient(name="Chicken", servings=100)],
            nutrition_info=NutritionInfo(calories=300)
        )
        mock_food_service.analyze_by_text.return_value = expected_result

        with patch('api.services.gemini_service.FoodAnalysisService', return_value=mock_food_service), \
             patch('api.services.gemini_service.ExerciseAnalysisService'):
            service = GeminiService()
            result = await service.analyze_food_by_text("Grilled chicken salad with tomatoes")
            
            # Verify the result
            assert result == expected_result
            mock_food_service.analyze_by_text.assert_called_once_with("Grilled chicken salad with tomatoes")

    @pytest.mark.asyncio
    async def test_analyze_food_by_image(self, mock_env, mock_food_service):
        """Test analyzing food by image."""
        expected_result = FoodAnalysisResult(
            food_name="Pizza",
            ingredients=[Ingredient(name="Cheese", servings=50)],
            nutrition_info=NutritionInfo(calories=450)
        )
        mock_food_service.analyze_by_image.return_value = expected_result
        mock_image_file = MagicMock()

        with patch('api.services.gemini_service.FoodAnalysisService', return_value=mock_food_service), \
             patch('api.services.gemini_service.ExerciseAnalysisService'):
            service = GeminiService()
            result = await service.analyze_food_by_image(mock_image_file)
            
            # Verify the result
            assert result == expected_result
            mock_food_service.analyze_by_image.assert_called_once_with(mock_image_file)

    @pytest.mark.asyncio
    async def test_analyze_nutrition_label(self, mock_env, mock_food_service):
        """Test analyzing nutrition label from image."""
        expected_result = FoodAnalysisResult(
            food_name="Nutrition Facts",
            ingredients=[],
            nutrition_info=NutritionInfo(calories=200, protein=15)
        )
        mock_food_service.analyze_nutrition_label.return_value = expected_result
        mock_image_file = MagicMock()

        with patch('api.services.gemini_service.FoodAnalysisService', return_value=mock_food_service), \
             patch('api.services.gemini_service.ExerciseAnalysisService'):
            service = GeminiService()
            result = await service.analyze_nutrition_label(mock_image_file, servings=2.0)
            
            # Verify the result
            assert result == expected_result
            mock_food_service.analyze_nutrition_label.assert_called_once_with(mock_image_file, 2.0)

    @pytest.mark.asyncio
    async def test_correct_food_analysis(self, mock_env, mock_food_service):
        """Test correcting food analysis based on user feedback."""
        previous_result = FoodAnalysisResult(
            food_name="Hambrger",  # Misspelled
            ingredients=[Ingredient(name="Beef patty", servings=100)],
            nutrition_info=NutritionInfo(calories=500)
        )
        
        expected_result = FoodAnalysisResult(
            food_name="Hamburger",  # Corrected
            ingredients=[Ingredient(name="Beef patty", servings=100)],
            nutrition_info=NutritionInfo(calories=500)
        )
        
        mock_food_service.correct_analysis.return_value = expected_result

        with patch('api.services.gemini_service.FoodAnalysisService', return_value=mock_food_service), \
             patch('api.services.gemini_service.ExerciseAnalysisService'):
            service = GeminiService()
            result = await service.correct_food_analysis(
                previous_result, 
                "It should be spelled Hamburger, not Hambrger"
            )
            
            # Verify the result
            assert result == expected_result
            mock_food_service.correct_analysis.assert_called_once_with(
                previous_result, 
                "It should be spelled Hamburger, not Hambrger"
            )

    # Exercise analysis tests

    @pytest.mark.asyncio
    async def test_analyze_exercise(self, mock_env, mock_exercise_service):
        """Test analyzing exercise with description and weight."""
        expected_result = ExerciseAnalysisResult(
            exercise_type="Running",
            duration="30 minutes",
            intensity="High",
            calories_burned=350
        )
        mock_exercise_service.analyze.return_value = expected_result

        with patch('api.services.gemini_service.FoodAnalysisService'), \
             patch('api.services.gemini_service.ExerciseAnalysisService', return_value=mock_exercise_service):
            service = GeminiService()
            result = await service.analyze_exercise("Running for 30 minutes", user_weight_kg=70.5)
            
            # Verify the result
            assert result == expected_result
            mock_exercise_service.analyze.assert_called_once_with("Running for 30 minutes", 70.5)

    @pytest.mark.asyncio
    async def test_analyze_exercise_without_weight(self, mock_env, mock_exercise_service):
        """Test analyzing exercise without user weight."""
        expected_result = ExerciseAnalysisResult(
            exercise_type="Yoga",
            duration="45 minutes",
            intensity="Medium",
            calories_burned=150
        )
        mock_exercise_service.analyze.return_value = expected_result

        with patch('api.services.gemini_service.FoodAnalysisService'), \
             patch('api.services.gemini_service.ExerciseAnalysisService', return_value=mock_exercise_service):
            service = GeminiService()
            result = await service.analyze_exercise("Yoga for 45 minutes")
            
            # Verify the result
            assert result == expected_result
            mock_exercise_service.analyze.assert_called_once_with("Yoga for 45 minutes", None)

    @pytest.mark.asyncio
    async def test_correct_exercise_analysis(self, mock_env, mock_exercise_service):
        """Test correcting exercise analysis based on user feedback."""
        previous_result = ExerciseAnalysisResult(
            exercise_type="Walking",
            duration="30 minutes",
            intensity="Low",
            calories_burned=120
        )
        
        expected_result = ExerciseAnalysisResult(
            exercise_type="Power Walking",
            duration="30 minutes",
            intensity="Medium",
            calories_burned=180
        )
        
        mock_exercise_service.correct_analysis.return_value = expected_result

        with patch('api.services.gemini_service.FoodAnalysisService'), \
             patch('api.services.gemini_service.ExerciseAnalysisService', return_value=mock_exercise_service):
            service = GeminiService()
            result = await service.correct_exercise_analysis(
                previous_result,
                "It was power walking at medium intensity, not regular walking"
            )
            
            # Verify the result
            assert result == expected_result
            mock_exercise_service.correct_analysis.assert_called_once_with(
                previous_result,
                "It was power walking at medium intensity, not regular walking"
            )

    @pytest.mark.asyncio
    async def test_service_errors(self, mock_env):
        """Test error handling in the service."""
        mock_food_service = MagicMock()
        mock_food_service.analyze_by_text = AsyncMock(side_effect=GeminiServiceException("API error"))

        with patch('api.services.gemini_service.FoodAnalysisService', return_value=mock_food_service), \
             patch('api.services.gemini_service.ExerciseAnalysisService'):
            service = GeminiService()
            
            with pytest.raises(GeminiServiceException) as exc_info:
                await service.analyze_food_by_text("Test food")
            
            assert "API error" in str(exc_info.value) 