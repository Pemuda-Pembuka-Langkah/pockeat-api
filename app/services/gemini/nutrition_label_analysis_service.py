import base64
from typing import Dict, Any
from app.services.gemini.base_gemini_service import BaseGeminiService, GeminiServiceException
from app.api.models.food_analysis import FoodAnalysisResult, NutritionInfo, Ingredient


class NutritionLabelAnalysisService(BaseGeminiService):
    """Service for analyzing nutrition label images using Gemini API."""
    
    def analyze(self, image_bytes: bytes, servings: float) -> FoodAnalysisResult:
        """
        Analyze a nutrition label image and estimate nutritional content.
        
        Args:
            image_bytes: The image bytes to analyze.
            servings: The number of servings the user will consume.
            
        Returns:
            A FoodAnalysisResult with the analysis details.
            
        Raises:
            GeminiServiceException: If there's an error analyzing the nutrition label.
        """
        try:
            prompt = f"""
            Analyze this nutrition label image. The user will consume {servings} servings.
            
            Please provide a comprehensive analysis including:
            - The name of the food
            - A complete list of ingredients with servings composition in grams
            - Detailed macronutrition information ONLY of calories, protein, carbs, fat, sodium, fiber, and sugar. No need to display other macro information.
            - Add warnings if the food contains high sodium (>500mg) or high sugar (>20g)
            
            Return your response as a strict JSON object with this exact format:
            {{
              "food_name": "string",
              "ingredients": [
                {{
                  "name": "string",
                  "servings": number
                }}
              ],
              "nutrition_info": {{
                "calories": number,
                "protein": number,
                "carbs": number,
                "fat": number,
                "sodium": number,
                "fiber": number,
                "sugar": number
              }},
              "warnings": ["string", "string"]
            }}
            
            IMPORTANT: Do not include any comments, annotations or notes in the JSON. Do not use '#' or '//' characters. Only return valid JSON.
            For the warnings array:
            - Include "High sodium content" (exact text) if sodium exceeds 500mg
            - Include "High sugar content" (exact text) if sugar exceeds 20g
            If there are no warnings, you can include an empty array [] for warnings.
            
            If no nutrition label is detected in the image or you cannot analyze it properly, use this format:
            {{
              "error": "No nutrition label detected",
              "food_name": "Unknown",
              "ingredients": [],
              "nutrition_info": {{
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0,
                "sodium": 0,
                "fiber": 0,
                "sugar": 0
              }},
              "warnings": []
            }}
            """
            
            # Prepare image data for Gemini
            # Base64 encode the image for the API
            image_part = {
                "mime_type": "image/jpeg", 
                "data": base64.b64encode(image_bytes).decode('utf-8')
            }
            
            # Create the content parts for the API request
            contents = [
                {"text": prompt},
                {"inline_data": image_part}
            ]
            
            response_text = self.generate_content(contents)
            return self._parse_food_response(response_text)
        except Exception as e:
            if isinstance(e, GeminiServiceException):
                raise
            raise GeminiServiceException(f"Error analyzing nutrition label: {str(e)}")
    
    def correct_analysis(self, previous_result: FoodAnalysisResult, user_comment: str, servings: float) -> FoodAnalysisResult:
        """
        Correct a nutrition label analysis based on user feedback.
        
        Args:
            previous_result: The previous food analysis result.
            user_comment: The user's correction comment.
            servings: The number of servings the user will consume.
            
        Returns:
            A corrected FoodAnalysisResult.
            
        Raises:
            GeminiServiceException: If there's an error correcting the analysis.
        """
        try:
            # Format ingredients for the prompt
            ingredients_str = ", ".join([f"{i.name}: {i.servings}g" for i in previous_result.ingredients])
            
            prompt = f"""
            Original nutrition label analysis (for {servings} servings):
            - Food name: {previous_result.food_name}
            - Ingredients: {ingredients_str}
            - Calories: {previous_result.nutrition_info.calories}
            - Protein: {previous_result.nutrition_info.protein}g
            - Carbs: {previous_result.nutrition_info.carbs}g
            - Fat: {previous_result.nutrition_info.fat}g
            - Sodium: {previous_result.nutrition_info.sodium}mg
            - Fiber: {previous_result.nutrition_info.fiber}g
            - Sugar: {previous_result.nutrition_info.sugar}g
            - Warnings: {", ".join(previous_result.warnings)}
            
            User correction comment: "{user_comment}"
            
            Please correct and analyze the ingredients and nutritional content on the correction comment.
            If it is about an ingredient or the food and not described, assume a standard serving size and ingredients for 1 person only.
            
            Provide a comprehensive analysis including:
            - The name of the food
            - A complete list of ingredients with servings composition (in grams) 
            - Detailed macronutrition information ONLY of calories, protein, carbs, fat, sodium, fiber, and sugar. No need to display other macro information.
            - Add warnings if the food contains high sodium (>500mg) or high sugar (>20g)
            
            Only modify values that need to be changed according to the user's feedback, but remember that the user CAN give more than one feedback.
            Please correct the analysis based on the user's comment accordingly.
            
            The corrected analysis should be for {servings} servings.
            
            Return your response as a strict JSON object with this exact format:
            {{
              "food_name": "string",
              "ingredients": [
                {{
                  "name": "string",
                  "servings": number
                }}
              ],
              "nutrition_info": {{
                "calories": number,
                "protein": number,
                "carbs": number,
                "fat": number,
                "sodium": number,
                "fiber": number,
                "sugar": number
              }},
              "warnings": ["string"]
            }}
            
            IMPORTANT: Do not include any comments, annotations or notes in the JSON. Do not use '#' or '//' characters. Only return valid JSON.
            For the warnings array:
            - Include "High sodium content" (exact text) if sodium exceeds 500mg
            - Include "High sugar content" (exact text) if sugar exceeds 20g
            If there are no warnings, you can include an empty array [] for warnings.
            """
            
            response_text = self.generate_content([prompt])
            return self._parse_food_response(response_text)
        except Exception as e:
            if isinstance(e, GeminiServiceException):
                raise
            raise GeminiServiceException(f"Error correcting nutrition label analysis: {str(e)}")
    
    def _parse_food_response(self, response_text: str) -> FoodAnalysisResult:
        """
        Parse the food analysis response from Gemini.
        
        Args:
            response_text: The text response from Gemini.
            
        Returns:
            A FoodAnalysisResult with the parsed data.
            
        Raises:
            GeminiServiceException: If parsing fails.
        """
        try:
            json_data = self.extract_json(response_text)
            
            # Check for error field
            if 'error' in json_data:
                raise GeminiServiceException(json_data['error'])
            
            # Extract the data
            food_name = json_data.get('food_name', 'Unknown')
            
            # Process ingredients
            ingredients_data = json_data.get('ingredients', [])
            ingredients = []
            for ingredient_data in ingredients_data:
                if isinstance(ingredient_data, dict):
                    name = ingredient_data.get('name', 'Unknown')
                    servings = ingredient_data.get('servings', 0.0)
                    ingredients.append(Ingredient(name=name, servings=float(servings)))
            
            # Process nutrition info
            nutrition_data = json_data.get('nutrition_info', {})
            nutrition_info = NutritionInfo(
                calories=int(nutrition_data.get('calories', 0)),
                protein=float(nutrition_data.get('protein', 0.0)),
                carbs=float(nutrition_data.get('carbs', 0.0)),
                fat=float(nutrition_data.get('fat', 0.0)),
                sodium=float(nutrition_data.get('sodium', 0.0)),
                fiber=float(nutrition_data.get('fiber', 0.0)),
                sugar=float(nutrition_data.get('sugar', 0.0))
            )
            
            # Process warnings
            warnings = json_data.get('warnings', [])
            is_low_confidence = json_data.get('is_low_confidence', False)
            
            # Check if there's a low confidence warning in the warnings
            if not is_low_confidence:
                for warning in warnings:
                    if 'confidence is low' in warning.lower():
                        is_low_confidence = True
                        break
            
            return FoodAnalysisResult(
                food_name=food_name,
                ingredients=ingredients,
                nutrition_info=nutrition_info,
                warnings=warnings,
                is_low_confidence=is_low_confidence
            )
        except Exception as e:
            if isinstance(e, GeminiServiceException):
                raise
            raise GeminiServiceException(f"Error parsing food analysis: {str(e)}") 