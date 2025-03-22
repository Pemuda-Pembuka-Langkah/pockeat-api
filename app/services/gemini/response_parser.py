"""
Service for parsing responses from the Gemini API.
"""
from app.utils.json_utils import parse_json_response, validate_json_schema
from app.utils.exceptions import InvalidJSONResponseError, ValidationError


class ResponseParser:
    """
    Service for parsing responses from the Gemini API.
    """
    
    @staticmethod
    def parse_food_analysis_response(response):
        """
        Parse a food analysis response from the Gemini API.
        
        Args:
            response: The response from the Gemini API
            
        Returns:
            dict: The parsed food analysis data
        """
        try:
            # Extract the text content from the response
            text_content = response.text
            
            # Parse the JSON from the response
            json_data = parse_json_response(text_content)
            
            # Define the expected schema
            schema = {
                "type": "object",
                "required": ["food", "calories"],
                "properties": {
                    "food": {"type": "string"},
                    "calories": {"type": "number"},
                    "protein": {"type": "number"},
                    "fat": {"type": "number"},
                    "carbs": {"type": "number"},
                    "portion_size": {"type": "string"},
                    "additional_info": {"type": "object"}
                }
            }
            
            # Validate the JSON against the schema
            if not validate_json_schema(json_data, schema):
                raise ValidationError("Response does not match expected schema")
            
            return json_data
        except Exception as e:
            raise InvalidJSONResponseError(str(e))
    
    @staticmethod
    def parse_exercise_analysis_response(response):
        """
        Parse an exercise analysis response from the Gemini API.
        
        Args:
            response: The response from the Gemini API
            
        Returns:
            dict: The parsed exercise analysis data
        """
        try:
            # Extract the text content from the response
            text_content = response.text
            
            # Parse the JSON from the response
            json_data = parse_json_response(text_content)
            
            # Define the expected schema
            schema = {
                "type": "object",
                "required": ["exercise", "calories_burned"],
                "properties": {
                    "exercise": {"type": "string"},
                    "calories_burned": {"type": "number"},
                    "duration_minutes": {"type": "number"},
                    "intensity": {"type": "string"},
                    "additional_info": {"type": "object"}
                }
            }
            
            # Validate the JSON against the schema
            if not validate_json_schema(json_data, schema):
                raise ValidationError("Response does not match expected schema")
            
            return json_data
        except Exception as e:
            raise InvalidJSONResponseError(str(e)) 