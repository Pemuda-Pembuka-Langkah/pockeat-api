"""
Food response parser for Gemini API.
"""

import logging
from typing import Dict, Any

from api.services.gemini.exceptions import GeminiParsingError
from api.services.gemini.utils.json_parser import extract_json_from_text, parse_json_safely
from api.models.food_analysis import FoodAnalysisResult, Ingredient, NutritionInfo

# Configure logger
logger = logging.getLogger(__name__)


class FoodResponseParser:
    """Parser for food analysis responses."""
    
    def parse_food_analysis_response(self, response_text: str, default_food_name: str) -> FoodAnalysisResult:
        """Parse the response from the Gemini API for food analysis.
        
        Args:
            response_text: The response text from the Gemini API.
            default_food_name: Default food name to use if parsing fails.
            
        Returns:
            The food analysis result.
            
        Raises:
            GeminiParsingError: If the response cannot be parsed.
        """
        try:
            # Extract JSON from the response
            json_str = extract_json_from_text(response_text)
            if not json_str:
                logger.warning("No JSON found in response, returning raw response")
                return FoodAnalysisResult(
                    food_name=default_food_name,
                    ingredients=[],
                    nutrition_info=NutritionInfo(),
                    warnings=[],
                    error=f"Failed to parse response: {response_text[:100]}..."
                )
            
            # Parse the JSON
            data = parse_json_safely(json_str)
            
            # Extract ingredients
            ingredients = []
            if "ingredients" in data and isinstance(data["ingredients"], list):
                for ing_data in data["ingredients"]:
                    if isinstance(ing_data, dict):
                        name = ing_data.get("name", "Unknown ingredient")
                        servings = float(ing_data.get("servings", 0))
                        ingredients.append(Ingredient(name=name, servings=servings))
            
            # Extract nutrition info
            nutrition_info = NutritionInfo()
            if "nutrition_info" in data and isinstance(data["nutrition_info"], dict):
                nutrition_data = data["nutrition_info"]
                nutrition_info = NutritionInfo(
                    calories=float(nutrition_data.get("calories", 0)),
                    protein=float(nutrition_data.get("protein", 0)),
                    carbs=float(nutrition_data.get("carbs", 0)),
                    fat=float(nutrition_data.get("fat", 0)),
                    sodium=float(nutrition_data.get("sodium", 0)),
                    fiber=float(nutrition_data.get("fiber", 0)),
                    sugar=float(nutrition_data.get("sugar", 0))
                )
            
            # Extract warnings
            warnings = []
            if "warnings" in data and isinstance(data["warnings"], list):
                warnings = [str(w) for w in data["warnings"]]
            
            # Extract error if present
            error = data.get("error")
            
            # Create and return the result
            result = FoodAnalysisResult(
                food_name=data.get("food_name", default_food_name),
                ingredients=ingredients,
                nutrition_info=nutrition_info,
                warnings=warnings,
                error=error
            )
            
            # Add standard warnings based on nutrition values
            result.add_standard_warnings()
            
            return result
        
        except Exception as e:
            logger.error(f"Error parsing food analysis response: {str(e)}")
            # Instead of raising an exception, return a result with the error
            return FoodAnalysisResult(
                food_name=default_food_name,
                ingredients=[],
                nutrition_info=NutritionInfo(),
                warnings=[],
                error=f"Failed to parse response: {str(e)}"
            ) 