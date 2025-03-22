"""
Service for analyzing food images using Gemini API.
"""
from app.services.gemini.prompt_service import PromptService
from app.services.gemini.response_parser import ResponseParser


class FoodAnalysisService:
    """
    Service for analyzing food images using Gemini API.
    """
    
    def __init__(self, gemini_client):
        """
        Initialize the food analysis service.
        
        Args:
            gemini_client: The Gemini API client
        """
        self.gemini_client = gemini_client
    
    def analyze_food_image(self, image_data):
        """
        Analyze a food image using Gemini API.
        
        Args:
            image_data (bytes): The image data
            
        Returns:
            dict: The food analysis data
        """
        # Get the prompt for food analysis
        prompt = self._format_prompt()
        
        # Generate content with the image
        response = self.gemini_client.generate_content_with_image(prompt, image_data)
        
        # Parse the response
        return ResponseParser.parse_food_analysis_response(response)
    
    def _format_prompt(self):
        """
        Format the prompt for food analysis.
        
        Returns:
            str: The formatted prompt
        """
        return PromptService.get_food_analysis_prompt() 