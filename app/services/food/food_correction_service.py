"""
Service for correcting food entries using Gemini API.
"""
from app.services.gemini.prompt_service import PromptService
from app.services.gemini.response_parser import ResponseParser


class FoodCorrectionService:
    """
    Service for correcting food entries using Gemini API.
    """
    
    def __init__(self, gemini_client):
        """
        Initialize the food correction service.
        
        Args:
            gemini_client: The Gemini API client
        """
        self.gemini_client = gemini_client
    
    def correct_food_entry(self, food_entry, user_correction):
        """
        Correct a food entry using Gemini API.
        
        Args:
            food_entry (str): The original food entry
            user_correction (str): The user's correction
            
        Returns:
            dict: The corrected food data
        """
        # Get the prompt for food correction
        prompt = self._format_prompt(food_entry, user_correction)
        
        # Generate content
        response = self.gemini_client.generate_content(prompt)
        
        # Parse the response
        return ResponseParser.parse_food_analysis_response(response)
    
    def _format_prompt(self, food_entry, user_correction):
        """
        Format the prompt for food correction.
        
        Args:
            food_entry (str): The original food entry
            user_correction (str): The user's correction
            
        Returns:
            str: The formatted prompt
        """
        return PromptService.get_food_correction_prompt(food_entry, user_correction) 