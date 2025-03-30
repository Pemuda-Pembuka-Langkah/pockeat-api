"""
Food correction service using Gemini API.
"""

import logging
from typing import Dict, Any

from api.services.gemini.exceptions import GeminiServiceException
from api.services.gemini.food.base_food_service import BaseFoodService
from api.models.food_analysis import FoodAnalysisResult

# Configure logger
logger = logging.getLogger(__name__)


class FoodCorrectionService(BaseFoodService):
    """Food correction service using Gemini API."""
    
    async def correct_food_analysis(self, previous_result: FoodAnalysisResult, user_comment: str) -> FoodAnalysisResult:
        """Correct a previous food analysis based on user feedback.
        
        Args:
            previous_result: The previous food analysis result.
            user_comment: The user's feedback.
            
        Returns:
            The corrected food analysis result.
            
        Raises:
            GeminiServiceException: If the correction fails.
        """
        logger.info(f"Correcting food analysis for {previous_result.food_name} with comment: {user_comment}")
        
        # Convert the previous result to a dict for the prompt
        previous_result_dict = previous_result.dict(exclude={"timestamp", "id"})
        
        # Generate the prompt for correction
        prompt = self.prompt_generator.generate_food_correction_prompt(previous_result_dict, user_comment)
        
        try:
            # Invoke the model
            response_text = await self._invoke_text_model(prompt)
            logger.debug(f"Received correction response: {response_text[:100]}...")
            
            # Parse the response
            corrected_result = self.response_parser.parse_food_analysis_response(response_text, previous_result.food_name)
            
            # Preserve the original ID
            corrected_result.id = previous_result.id
            
            return corrected_result
        except GeminiServiceException:
            # Re-raise GeminiServiceExceptions
            raise
        except Exception as e:
            logger.error(f"Error in correct_food_analysis: {str(e)}")
            error_message = f"Failed to correct food analysis: {str(e)}"
            
            # Return original result with error
            previous_result.error = error_message
            return previous_result
    
    async def correct_nutrition_label(self, previous_result: FoodAnalysisResult, user_comment: str, servings: float = 1.0) -> FoodAnalysisResult:
        """Correct a previous nutrition label analysis based on user feedback.
        
        Args:
            previous_result: The previous food analysis result.
            user_comment: The user's feedback.
            servings: The number of servings.
            
        Returns:
            The corrected food analysis result.
            
        Raises:
            GeminiServiceException: If the correction fails.
        """
        logger.info(f"Correcting nutrition label analysis for {previous_result.food_name} with comment: {user_comment}")
        
        # Convert the previous result to a dict for the prompt
        previous_result_dict = previous_result.dict(exclude={"timestamp", "id"})
        
        # Generate the prompt for nutrition label correction
        prompt = self.prompt_generator.generate_nutrition_label_correction_prompt(previous_result_dict, user_comment, servings)
        
        try:
            # Invoke the model
            response_text = await self._invoke_text_model(prompt)
            logger.debug(f"Received correction response: {response_text[:100]}...")
            
            # Parse the response
            corrected_result = self.response_parser.parse_food_analysis_response(response_text, previous_result.food_name)
            
            # Preserve the original ID
            corrected_result.id = previous_result.id
            
            return corrected_result
        except GeminiServiceException:
            # Re-raise GeminiServiceExceptions
            raise
        except Exception as e:
            logger.error(f"Error in correct_nutrition_label: {str(e)}")
            error_message = f"Failed to correct nutrition label analysis: {str(e)}"
            
            # Return original result with error
            previous_result.error = error_message
            return previous_result 