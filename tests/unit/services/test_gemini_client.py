"""
Tests for the Gemini API client service.
"""
import pytest
from unittest.mock import patch, MagicMock

# Import the service that doesn't exist yet (RED phase)
from app.services.gemini.gemini_client import GeminiClient


class TestGeminiClient:
    """Test suite for the GeminiClient class."""

    def test_initialization(self):
        """Test that the client initializes with API key."""
        # RED: This will fail because the service doesn't exist yet
        client = GeminiClient(api_key="test_api_key")
        assert client.api_key == "test_api_key"
        
    @patch('app.services.gemini.gemini_client.genai')
    def test_configure_model(self, mock_genai):
        """Test that the model is configured correctly."""
        # RED: This will fail because the service doesn't exist yet
        client = GeminiClient(api_key="test_api_key")
        client.configure_model()
        
        # Assert genai was configured with API key
        mock_genai.configure.assert_called_once_with(api_key="test_api_key")
    
    @patch('app.services.gemini.gemini_client.genai.GenerativeModel')
    def test_generate_content_text(self, mock_generative_model):
        """Test generating content with text-only prompt."""
        # Setup mock
        mock_model = MagicMock()
        mock_generative_model.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = "Generated response"
        mock_model.generate_content.return_value = mock_response
        
        # RED: This will fail because the service doesn't exist yet
        client = GeminiClient(api_key="test_api_key")
        response = client.generate_content("Sample prompt")
        
        # Assertions
        mock_model.generate_content.assert_called_once_with("Sample prompt")
        assert response.text == "Generated response"
    
    @patch('app.services.gemini.gemini_client.genai.GenerativeModel')
    def test_generate_content_with_image(self, mock_generative_model):
        """Test generating content with an image in the prompt."""
        # Setup mock
        mock_model = MagicMock()
        mock_generative_model.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = "Image analysis response"
        mock_model.generate_content.return_value = mock_response
        
        # RED: This will fail because the service doesn't exist yet
        client = GeminiClient(api_key="test_api_key", model_name="gemini-pro-vision")
        response = client.generate_content_with_image(
            "Analyze this food image", 
            image_data=b"fake_image_bytes"
        )
        
        # Assertions
        assert response.text == "Image analysis response"
        # Note: We can't easily test the exact arguments because the image
        # processing depends on the actual implementation 