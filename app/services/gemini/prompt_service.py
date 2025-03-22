"""
Service for managing prompts for the Gemini API.
"""


class PromptService:
    """
    Service for managing prompts for the Gemini API.
    """
    
    @staticmethod
    def get_food_analysis_prompt():
        """
        Get the prompt for food image analysis.
        
        Returns:
            str: The prompt for food image analysis
        """
        return """
        You are a nutrition expert. Analyze this food image and provide detailed nutritional information.
        
        Be specific about the food items you can identify in the image.
        
        Provide your response in the following JSON format:
        {
            "food": "Name of the food",
            "calories": number (per serving),
            "protein": number (grams per serving),
            "fat": number (grams per serving),
            "carbs": number (grams per serving),
            "portion_size": "description of portion size",
            "additional_info": {
                "food_group": "e.g., fruits, vegetables, grains, proteins, dairy",
                "vitamins": ["list of significant vitamins"],
                "minerals": ["list of significant minerals"]
            }
        }
        
        Return ONLY the JSON object without any additional explanation.
        """
    
    @staticmethod
    def get_food_correction_prompt(food_entry, user_correction):
        """
        Get the prompt for food entry correction.
        
        Args:
            food_entry (str): The original food entry
            user_correction (str): The user's correction
            
        Returns:
            str: The prompt for food correction
        """
        return f"""
        You are a nutrition expert. The user has made the following food entry:
        
        "{food_entry}"
        
        The user has provided this correction or additional information:
        
        "{user_correction}"
        
        Based on this information, provide the corrected food entry with nutritional details.
        
        Provide your response in the following JSON format:
        {
            "food": "Corrected name of the food",
            "calories": number (per serving),
            "protein": number (grams per serving),
            "fat": number (grams per serving),
            "carbs": number (grams per serving),
            "portion_size": "description of portion size"
        }
        
        Return ONLY the JSON object without any additional explanation.
        """
    
    @staticmethod
    def get_exercise_analysis_prompt(description):
        """
        Get the prompt for exercise analysis.
        
        Args:
            description (str): The exercise description
            
        Returns:
            str: The prompt for exercise analysis
        """
        return f"""
        You are a fitness expert. The user has described the following exercise:
        
        "{description}"
        
        Analyze this exercise description and provide details about the exercise, including estimated calories burned.
        
        Provide your response in the following JSON format:
        {
            "exercise": "Name of the exercise",
            "calories_burned": number (estimated calories burned),
            "duration_minutes": number (if specified, otherwise estimate),
            "intensity": "light, moderate, or intense",
            "additional_info": {
                "muscle_groups": ["list of primary muscle groups targeted"],
                "exercise_type": "e.g., cardio, strength, flexibility",
                "recommendations": "brief recommendations for improvement"
            }
        }
        
        Return ONLY the JSON object without any additional explanation.
        """
    
    @staticmethod
    def get_exercise_correction_prompt(exercise_entry, user_correction):
        """
        Get the prompt for exercise entry correction.
        
        Args:
            exercise_entry (str): The original exercise entry
            user_correction (str): The user's correction
            
        Returns:
            str: The prompt for exercise correction
        """
        return f"""
        You are a fitness expert. The user has made the following exercise entry:
        
        "{exercise_entry}"
        
        The user has provided this correction or additional information:
        
        "{user_correction}"
        
        Based on this information, provide the corrected exercise entry with details.
        
        Provide your response in the following JSON format:
        {
            "exercise": "Corrected name of the exercise",
            "calories_burned": number (estimated calories burned),
            "duration_minutes": number,
            "intensity": "light, moderate, or intense"
        }
        
        Return ONLY the JSON object without any additional explanation.
        """ 