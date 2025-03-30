"""
Food text analysis service using Gemini API.
"""

import logging
from typing import Dict, Any

from api.services.gemini.exceptions import GeminiServiceException
from api.services.gemini.food.base_food_service import BaseFoodService
from api.models.food_analysis import FoodAnalysisResult, NutritionInfo

# Configure logger
logger = logging.getLogger(__name__)


class FoodTextAnalysisService(BaseFoodService):
    """Food text analysis service using Gemini API."""
    
    async def analyze(self, description: str) -> FoodAnalysisResult:
        """Analyze food from a text description.
        
        Args:
            description: The food description.
            
        Returns:
            The food analysis result.
            
        Raises:
            GeminiServiceException: If the analysis fails.
        """
        logger.info(f"Analyzing food from text: {description[:50]}...")
        
        # Generate the prompt for food analysis
        prompt_text = self.prompt_generator.generate_food_text_analysis_prompt(description)
        
        try:
            # Invoke the model
            response_text = await self._invoke_text_model(prompt_text)
            logger.debug(f"Received response: {response_text[:100]}...")
            
            # Parse the response
            return self.response_parser.parse_food_analysis_response(response_text, description)
        except GeminiServiceException:
            # Re-raise GeminiServiceExceptions
            raise
        except Exception as e:
            logger.error(f"Error in analyze: {str(e)}")
            error_message = f"Failed to analyze food text: {str(e)}"
            
            # Return result with error
            return FoodAnalysisResult(
                food_name="Unknown",
                ingredients=[],
                nutrition_info=NutritionInfo(),
                warnings=[],
                error=error_message
            ) 