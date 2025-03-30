"""
Base food analysis service using Gemini API.
"""

import logging
import base64
import io
from typing import Dict, Any, Optional

from api.services.gemini.base_service import BaseLangChainService
from api.services.gemini.exceptions import GeminiServiceException, InvalidImageError
from api.services.gemini.food.prompt_generator import FoodPromptGenerator
from api.services.gemini.food.response_parser import FoodResponseParser
from api.models.food_analysis import FoodAnalysisResult

# Configure logger
logger = logging.getLogger(__name__)


class BaseFoodService(BaseLangChainService):
    """Base food analysis service using Gemini API."""
    
    def __init__(self):
        """Initialize the service."""
        super().__init__()
        self.prompt_generator = FoodPromptGenerator()
        self.response_parser = FoodResponseParser()
        logger.info(f"Initializing {self.__class__.__name__}")
    
    def _read_image_bytes(self, image_file) -> str:
        """Read image bytes and convert to base64 for the Gemini API.
        
        Args:
            image_file: The image file (file-like object).
            
        Returns:
            Base64-encoded image data.
            
        Raises:
            InvalidImageError: If the image file is invalid.
        """
        try:
            # If the image file is a bytes-like object, use it directly
            if isinstance(image_file, bytes):
                image_bytes = image_file
            # If it's a file-like object, read it
            elif hasattr(image_file, 'read'):
                # Check if it has a seek method and use it to rewind the file
                if hasattr(image_file, 'seek'):
                    image_file.seek(0)
                image_bytes = image_file.read()
            else:
                # For other cases, try to open and read the file
                with open(image_file, 'rb') as f:
                    image_bytes = f.read()
            
            # Convert to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            return base64_image
        except Exception as e:
            error_message = f"Invalid image file: {str(e)}"
            logger.error(error_message)
            raise InvalidImageError(error_message)
    
    async def _invoke_multimodal_model(self, prompt: str, image_base64: str) -> str:
        """Invoke the Gemini multimodal model with a prompt and an image.
        
        Args:
            prompt: The prompt to send to the Gemini API.
            image_base64: The base64-encoded image data.
            
        Returns:
            The response text from the Gemini API.
            
        Raises:
            GeminiServiceException: If the invocation fails.
        """
        try:
            # Get the response from the multimodal model
            response = await self.vision_llm.ainvoke({
                "prompt": prompt,
                "image": image_base64
            })
            
            # Return the response text
            return response
        except Exception as e:
            error_message = f"Failed to invoke multimodal model: {str(e)}"
            logger.error(error_message)
            raise GeminiServiceException(error_message) 