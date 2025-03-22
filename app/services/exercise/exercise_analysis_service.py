"""
Service for analyzing exercise descriptions using Gemini API.
"""
from app.services.gemini.prompt_service import PromptService
from app.services.gemini.response_parser import ResponseParser


class ExerciseAnalysisService:
    """
    Service for analyzing exercise descriptions using Gemini API.
    """
    
    def __init__(self, gemini_client):
        """
        Initialize the exercise analysis service.
        
        Args:
            gemini_client: The Gemini API client
        """
        self.gemini_client = gemini_client
    
    def analyze_exercise(self, description):
        """
        Analyze an exercise description using Gemini API.
        
        Args:
            description (str): The exercise description
            
        Returns:
            dict: The exercise analysis data
        """
        # Get the prompt for exercise analysis
        prompt = self._format_prompt(description)
        
        # Generate content
        response = self.gemini_client.generate_content(prompt)
        
        # Parse the response
        return ResponseParser.parse_exercise_analysis_response(response)
    
    def _format_prompt(self, description):
        """
        Format the prompt for exercise analysis.
        
        Args:
            description (str): The exercise description
            
        Returns:
            str: The formatted prompt
        """
        return PromptService.get_exercise_analysis_prompt(description) 