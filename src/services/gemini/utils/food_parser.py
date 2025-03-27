"""
Parser for food analysis responses from Gemini.
"""

import json
import re
from typing import Any, Dict

from src.models.food_analysis import FoodAnalysisResult

class FoodAnalysisParser:
    """Parser for food analysis responses from Gemini."""
    
    @staticmethod
    def parse(text_output: str) -> FoodAnalysisResult:
        """Parse a food analysis response from Gemini.
        
        Args:
            text_output: The text output from Gemini.
            
        Returns:
            A FoodAnalysisResult object.
        """
        try:
            # Clean up the text output
            text_output = text_output.strip()
            
            # Try to extract JSON from the text
            json_match = re.search(r'({.*})', text_output, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = text_output
            
            # Log the raw JSON string for debugging
            print(f"Raw food analysis response from Gemini: {json_str}")
            
            # Clean problematic JSON formatting
            json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
            
            # Parse the JSON - if this fails, it will raise an exception
            data = json.loads(json_str)
            
            # Simply return the data as is, preserving any error keys from Gemini
            return FoodAnalysisResult.from_dict(data)
            
        except Exception as e:
            print(f"Failed to parse Gemini response: {str(e)}")
            print(f"Raw response: {text_output}")
            
            # Create error response
            error_data = {
                "error": f"Invalid response from Gemini: {str(e)}",
                "food_name": "Unknown",
                "ingredients": [],
                "nutrition_info": {
                    "calories": 0,
                    "protein": 0,
                    "carbs": 0,
                    "fat": 0,
                    "sodium": 0,
                    "fiber": 0,
                    "sugar": 0
                },
                "warnings": []
            }
            return FoodAnalysisResult.from_dict(error_data) 