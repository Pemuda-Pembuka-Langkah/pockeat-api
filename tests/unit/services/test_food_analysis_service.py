"""
Tests for the Food Analysis Service.
"""
import pytest
from unittest.mock import patch, MagicMock

# Import the service that doesn't exist yet (RED phase)
from app.services.food.food_analysis_service import FoodAnalysisService


class TestFoodAnalysisService:
    """Test suite for the FoodAnalysisService class."""

    def test_initialization(self):
        """Test that the service initializes with Gemini client."""
        # Setup mock
        mock_gemini_client = MagicMock()
        
        # RED: This will fail because the service doesn't exist yet
        service = FoodAnalysisService(gemini_client=mock_gemini_client)
        assert service.gemini_client == mock_gemini_client
    
    @patch('app.services.food.food_analysis_service.FoodAnalysisService._format_prompt')
    def test_analyze_food_image(self, mock_format_prompt):
        """Test analyzing food image."""
        # Setup mocks
        mock_gemini_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"food": "Apple", "calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14}'
        mock_gemini_client.generate_content_with_image.return_value = mock_response
        mock_format_prompt.return_value = "Analyze this food image"
        
        # RED: This will fail because the service doesn't exist yet
        service = FoodAnalysisService(gemini_client=mock_gemini_client)
        result = service.analyze_food_image(image_data=b"fake_image_bytes")
        
        # Assertions
        mock_gemini_client.generate_content_with_image.assert_called_once()
        assert isinstance(result, dict)
        assert result["food"] == "Apple"
        assert result["calories"] == 52
    
    def test_format_prompt(self):
        """Test that the prompt is correctly formatted."""
        # Setup mock
        mock_gemini_client = MagicMock()
        
        # RED: This will fail because the service doesn't exist yet
        service = FoodAnalysisService(gemini_client=mock_gemini_client)
        prompt = service._format_prompt()
        
        # Assertions
        assert "JSON" in prompt
        assert "food" in prompt
        assert "calories" in prompt 