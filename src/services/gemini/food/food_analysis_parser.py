"""
Parser for food analysis results from Gemini.
"""

import json
import re
from typing import Dict, Any

from src.models.food_analysis import FoodAnalysisResult
from src.services.gemini.exceptions import GeminiServiceException


class FoodAnalysisParser:
    """Parser for food analysis results from Gemini."""
    
    @staticmethod
    def parse(text_output: str) -> FoodAnalysisResult:
        """Parse a food analysis result from the Gemini output.
        
        Args:
            text_output: The text output from the Gemini model.
            
        Returns:
            The food analysis result.
            
        Raises:
            GeminiServiceException: If the parsing fails.
        """
        try:
            # Try to extract JSON from the text
            json_match = re.search(r'({.*})', text_output, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = text_output
            
            # Parse the JSON
            analysis_dict = json.loads(json_str)
            
            # Create a FoodAnalysisResult from the dictionary
            return FoodAnalysisResult.from_dict(analysis_dict)
        
        except Exception as e:
            raise GeminiServiceException(f"Failed to parse food analysis result: {str(e)}")

    @staticmethod
    def parse_json(json_text: str) -> FoodAnalysisResult:
        """Parse a JSON string into a FoodAnalysisResult.
        
        Args:
            json_text: The JSON string.
            
        Returns:
            The FoodAnalysisResult.
            
        Raises:
            GeminiServiceException: If the JSON is invalid.
        """
        try:
            # Handle empty input
            if not json_text or json_text.strip() == '':
                raise ValueError("Empty input")
            
            # Parse the JSON
            json_data = json.loads(json_text)
            
            # Check if json_data is a dict
            if not isinstance(json_data, dict):
                raise ValueError(f"Expected JSON object, got {type(json_data)}")
            
            # Check for error field
            if 'error' in json_data:
                if isinstance(json_data['error'], str):
                    raise GeminiServiceException(json_data['error'])
                elif isinstance(json_data['error'], dict) and 'message' in json_data['error']:
                    raise GeminiServiceException(json_data['error']['message'])
                else:
                    raise GeminiServiceException('Unknown error in response')
            
            # Handle ingredients safely
            if 'ingredients' in json_data and isinstance(json_data['ingredients'], list):
                valid_ingredients = []
                for item in json_data['ingredients']:
                    if isinstance(item, dict):
                        valid_ingredients.append(item)
                json_data['ingredients'] = valid_ingredients
            
            # Check for low confidence warnings
            has_low_confidence_warning = (
                'warnings' in json_data 
                and isinstance(json_data['warnings'], list)
                and any('confidence is low' in warning.lower() for warning in json_data['warnings'] 
                        if isinstance(warning, str))
            )
            
            # Set the low confidence flag if needed
            if has_low_confidence_warning and 'is_low_confidence' not in json_data:
                json_data['is_low_confidence'] = True
            
            # Create the FoodAnalysisResult
            return FoodAnalysisResult.from_dict(json_data)
        
        except Exception as e:
            # Propagate GeminiServiceException
            if isinstance(e, GeminiServiceException):
                raise
            
            # Wrap other exceptions
            raise GeminiServiceException(f"Error parsing food analysis: {str(e)}") 