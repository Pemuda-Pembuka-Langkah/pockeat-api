"""
Tests for the BaseLangChainService class.
"""

import os
import sys
import base64
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from io import BytesIO

# Add the project root directory to the Python path so we can import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from api.services.gemini.base_service import BaseLangChainService
from api.services.gemini.exceptions import GeminiAPIKeyMissingError, InvalidImageError


class TestBaseLangChainService:
    """Test suite for the BaseLangChainService class."""

    @pytest.fixture
    def mock_env(self):
        """Set up environment variables for testing."""
        original_env = os.environ.copy()
        os.environ["GOOGLE_API_KEY"] = "test-api-key"
        yield
        os.environ.clear()
        os.environ.update(original_env)

    @pytest.fixture
    def mock_langchain_llm(self):  # pragma: no cover
        """Mock LangChain LLM."""
        mock = MagicMock()
        # Set up async mock for ainvoke
        mock.ainvoke = AsyncMock()
        response = MagicMock()
        response.content = '{"test_key": "test_value"}'
        mock.ainvoke.return_value = response
        return mock

    def test_init_missing_api_key(self):
        """Test initialization with missing API key."""
        with patch.dict(os.environ, clear=True):
            with pytest.raises(GeminiAPIKeyMissingError):
                BaseLangChainService()

    def test_init_with_api_key(self, mock_env):
        """Test successful initialization with API key."""
        with patch('api.services.gemini.base_service.ChatGoogleGenerativeAI') as mock_chat:
            service = BaseLangChainService()
            assert service is not None
            assert service.text_model_name == "models/gemini-1.5-pro"
            assert service.multimodal_model_name == "models/gemini-1.5-pro"
            assert service.text_llm is not None
            assert service.multimodal_llm is not None

    def test_init_with_custom_model_names(self, mock_env):
        """Test initialization with custom model names."""
        with patch('api.services.gemini.base_service.ChatGoogleGenerativeAI'):
            service = BaseLangChainService(
                text_model_name="custom-text-model",
                multimodal_model_name="custom-multimodal-model"
            )
            assert service.text_model_name == "custom-text-model"
            assert service.multimodal_model_name == "custom-multimodal-model"

    def test_read_image_bytes_success(self, mock_env):
        """Test successful image bytes reading."""
        with patch('api.services.gemini.base_service.ChatGoogleGenerativeAI'):
            service = BaseLangChainService()
            
            # Create a simple image file
            image_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100  # Simulated PNG header and content
            mock_file = BytesIO(image_data)
            
            # Call the method and validate result
            base64_str = service._read_image_bytes(mock_file)
            
            # Check that it's a valid base64 string
            assert isinstance(base64_str, str)
            # Should be able to decode it back
            decoded = base64.b64decode(base64_str)
            assert decoded == image_data

    def test_read_image_bytes_empty_file(self, mock_env):
        """Test reading an empty image file."""
        with patch('api.services.gemini.base_service.ChatGoogleGenerativeAI'):
            service = BaseLangChainService()
            mock_file = BytesIO(b'')
            
            with pytest.raises(InvalidImageError, match="Image file is empty"):
                service._read_image_bytes(mock_file)

    def test_read_image_bytes_string_input(self, mock_env):
        """Test reading image from string input instead of bytes."""
        with patch('api.services.gemini.base_service.ChatGoogleGenerativeAI'):
            service = BaseLangChainService()
            
            # Create a mock file with string content
            class MockStringFile:
                def read(self):
                    return "not bytes but string"
            
            mock_file = MockStringFile()
            
            # Should convert to bytes
            base64_str = service._read_image_bytes(mock_file)
            assert isinstance(base64_str, str)
            
            # Should be decodable
            decoded = base64.b64decode(base64_str)
            assert decoded == b"not bytes but string"

    def test_read_image_bytes_exception(self, mock_env):
        """Test handling of exceptions during image reading."""
        with patch('api.services.gemini.base_service.ChatGoogleGenerativeAI'):
            service = BaseLangChainService()
            
            # Create a mock file that raises an exception
            class MockErrorFile:
                def read(self):
                    raise IOError("Test IO error")
            
            mock_file = MockErrorFile()
            
            with pytest.raises(InvalidImageError, match="Failed to process image: Test IO error"):
                service._read_image_bytes(mock_file)

    @pytest.mark.asyncio
    async def test_invoke_text_model(self, mock_env):
        """Test invoking the text model."""
        # Create a proper AsyncMock for the LLM
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock()
        
        # Configure the mock response
        mock_response = MagicMock()
        mock_response.content = "Test response from model"
        mock_llm.ainvoke.return_value = mock_response
        
        with patch('api.services.gemini.base_service.ChatGoogleGenerativeAI'):
            service = BaseLangChainService()
            # Replace the LLM with our mock
            service.text_llm = mock_llm
            
            result = await service._invoke_text_model("Test prompt")
            
            # Verify correct response
            assert result == "Test response from model"
            
            # Verify the LLM was called correctly
            mock_llm.ainvoke.assert_called_once()
            # Check we're passing a HumanMessage
            args = mock_llm.ainvoke.call_args[0][0]
            assert len(args) == 1
            assert args[0].content == "Test prompt"

    @pytest.mark.asyncio
    async def test_invoke_text_model_error(self, mock_env):
        """Test error handling when invoking the text model."""
        # Create a proper AsyncMock for the LLM
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("Model API error"))
        
        with patch('api.services.gemini.base_service.ChatGoogleGenerativeAI'):
            service = BaseLangChainService()
            # Replace the LLM with our mock
            service.text_llm = mock_llm
            
            with pytest.raises(Exception, match="Model API error"):
                await service._invoke_text_model("Test prompt")

    @pytest.mark.asyncio
    async def test_invoke_multimodal_model(self, mock_env):
        """Test invoking the multimodal model with text and image."""
        # Create a proper AsyncMock for the LLM
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock()
        
        # Configure the mock response
        mock_response = MagicMock()
        mock_response.content = "Test response from multimodal model"
        mock_llm.ainvoke.return_value = mock_response
        
        with patch('api.services.gemini.base_service.ChatGoogleGenerativeAI'):
            service = BaseLangChainService()
            # Replace the LLM with our mock
            service.multimodal_llm = mock_llm
            
            result = await service._invoke_multimodal_model("Describe this image", "base64_image_string")
            
            # Verify correct response
            assert result == "Test response from multimodal model"
            
            # Verify the LLM was called correctly
            mock_llm.ainvoke.assert_called_once()
            
            # Check we're passing a HumanMessage with correct content structure
            args = mock_llm.ainvoke.call_args[0][0]
            assert len(args) == 1
            content = args[0].content
            assert len(content) == 2
            assert content[0]["type"] == "text"
            assert content[0]["text"] == "Describe this image"
            assert content[1]["type"] == "image_url"
            assert "base64_image_string" in content[1]["image_url"]["url"]

    @pytest.mark.asyncio
    async def test_invoke_multimodal_model_error(self, mock_env):
        """Test error handling when invoking the multimodal model."""
        # Create a proper AsyncMock for the LLM
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("Multimodal API error"))
        
        with patch('api.services.gemini.base_service.ChatGoogleGenerativeAI'):
            service = BaseLangChainService()
            # Replace the LLM with our mock
            service.multimodal_llm = mock_llm
            
            with pytest.raises(Exception, match="Multimodal API error"):
                await service._invoke_multimodal_model("Describe this image", "base64_image_string") 