"""
Food image analysis service using Gemini API.
"""

import logging
from typing import Dict, Any

from api.services.gemini.exceptions import GeminiServiceException, InvalidImageError
from api.services.gemini.food.base_food_service import BaseFoodService
from api.models.food_analysis import FoodAnalysisResult, NutritionInfo

# Configure logger
logger = logging.getLogger(__name__)


class FoodImageAnalysisService(BaseFoodService):
    """Food image analysis service using Gemini API."""
    
    async def analyze(self, image_file) -> FoodAnalysisResult:
        """Analyze food from an image.
        
        Args:
            image_file: The image file (file-like object).
            
        Returns:
            The food analysis result.
            
        Raises:
            GeminiServiceException: If the analysis fails.
        """
        if not image_file:
            error_message = "No image file provided"
            logger.error(error_message)
            return FoodAnalysisResult(
                food_name="Unknown",
                ingredients=[],
                nutrition_info=NutritionInfo(),
                warnings=[],
                error=error_message
            )
        
        logger.info(f"Analyzing food from image: {getattr(image_file, 'filename', 'unknown')}")
        
        try:
            # Read image bytes
            image_base64 = self._read_image_bytes(image_file)
            
            # Generate the prompt for food image analysis
            prompt = self.prompt_generator.generate_food_image_analysis_prompt()
            
            # Invoke the multimodal model
            response_text = await self._invoke_multimodal_model(prompt, image_base64)
            logger.debug(f"Received response: {response_text[:100]}...")
            
            # Parse the response
            return self.response_parser.parse_food_analysis_response(response_text, "Food Image")
        except InvalidImageError as e:
            # Handle image processing errors
            logger.error(f"Invalid image error: {str(e)}")
            return FoodAnalysisResult(
                food_name="Unknown",
                ingredients=[],
                nutrition_info=NutritionInfo(),
                warnings=[],
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Error in analyze: {str(e)}")
            error_message = f"Failed to analyze food image: {str(e)}"
            
            # Return result with error
            return FoodAnalysisResult(
                food_name="Unknown",
                ingredients=[],
                nutrition_info=NutritionInfo(),
                warnings=[],
                error=error_message
            ) 