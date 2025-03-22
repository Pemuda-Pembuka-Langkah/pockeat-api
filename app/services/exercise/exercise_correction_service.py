"Service for correcting exercise entries using Gemini API."
from app.services.gemini.prompt_service import PromptService
from app.services.gemini.response_parser import ResponseParser


class ExerciseCorrectionService:
    """
    Service for correcting exercise entries using Gemini API.
    """
    
    def __init__(self, gemini_client):
        """
        Initialize the exercise correction service.
        
        Args:
            gemini_client: The Gemini API client
        """
        self.gemini_client = gemini_client
    
    def correct_exercise_entry(self, exercise_entry, user_correction):
        """
        Correct an exercise entry using Gemini API.
        
        Args:
            exercise_entry (str): The original exercise entry
            user_correction (str): The user's correction
            
        Returns:
            dict: The corrected exercise data
        """
        # Get the prompt for exercise correction
        prompt = self._format_prompt(exercise_entry, user_correction)
        
        # Generate content
        response = self.gemini_client.generate_content(prompt)
        
        # Parse the response
        return ResponseParser.parse_exercise_analysis_response(response)
    
    def _format_prompt(self, exercise_entry, user_correction):
        """
        Format the prompt for exercise correction.
        
        Args:
            exercise_entry (str): The original exercise entry
            user_correction (str): The user's correction
            
        Returns:
            str: The formatted prompt
        """
        return PromptService.get_exercise_correction_prompt(exercise_entry, user_correction)
