import base64
from typing import Dict, Any
from app.services.gemini.base_gemini_service import BaseGeminiService, GeminiServiceException
from app.api.models.food_analysis import FoodAnalysisResult, NutritionInfo, Ingredient


class FoodImageAnalysisService(BaseGeminiService):
    """Service for analyzing food images using Gemini API."""
    
    def analyze(self, image_bytes: bytes) -> FoodAnalysisResult:
        """
        Analyze a food image and estimate nutritional content.
        
        Args:
            image_bytes: The image bytes to analyze.
            
        Returns:
            A FoodAnalysisResult with the analysis details.
            
        Raises:
            GeminiServiceException: If there's an error analyzing the food image.
        """
        try:
            prompt = """
            You are a food recognition and nutrition analysis expert. Carefully analyze this image and identify any food or meal present.
            
            Please look for:
            - Prepared meals
            - Individual food items
            - Snacks
            - Beverages
            - Fruits and vegetables
            - Packaged food products
            - Amount of food items
            
            Even if the image quality is not perfect or the food is partially visible, please do your best to identify it and provide an analysis.
            
            For the identified food, provide a comprehensive analysis including:
            - The specific name of the food
            - A detailed list of likely ingredients with estimated servings composition in grams, estimate based on size and portion to the best of your ability.
            - Detailed macronutrition information ONLY of calories, protein, carbs, fat, sodium, fiber, and sugar. No need to display other macro information.
            - Add warnings if the food contains high sodium (>500mg) or high sugar (>20g)
            
            BE VERY THOROUGH. YOU WILL BE FIRED. THE CUSTOMER CAN GET POISONED. BE VERY THOROUGH.
            Return your response as a strict JSON object with this exact format with NO COMMENTS:
            {
              "food_name": "string",
              "ingredients": [
                {
                  "name": "string",
                  "servings": number
                }
              ],
              "nutrition_info": {
                "calories": number,
                "protein": number,
                "carbs": number,
                "fat": number,
                "sodium": number,
                "fiber": number,
                "sugar": number
              },
              "warnings": ["string", "string"]
            }
            
            IMPORTANT: Do not include any comments, annotations or notes in the JSON. Do not use '#' or '//' characters. Only return valid JSON.
            For the warnings array:
            - Include "High sodium content" (exact text) if sodium exceeds 500mg
            - Include "High sugar content" (exact text) if sugar exceeds 20g
            If there are no warnings, you can include an empty array [] for warnings.
            
            If absolutely no food can be detected in the image, only then use this format:
            {
              "error": "No food detected in image",
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
            raise GeminiServiceException(f"Error analyzing food from image: {str(e)}")
    
    def correct_analysis(self, previous_result: FoodAnalysisResult, user_comment: str) -> FoodAnalysisResult:
        """
        Correct a food analysis based on user feedback.
        
        Args:
            previous_result: The previous food analysis result.
            user_comment: The user's correction comment.
            
        Returns:
            A corrected FoodAnalysisResult.
            
        Raises:
            GeminiServiceException: If there's an error correcting the analysis.
        """
        try:
            # Format the previous analysis result for the prompt
            formatted_previous_result = self._format_food_analysis_result(previous_result)
            
            prompt = f"""
            You are a food nutrition expert tasked with correcting a food analysis based on user feedback.
            
            ORIGINAL ANALYSIS:
            {formatted_previous_result}
            
            USER CORRECTION: "{user_comment}"
            
            INSTRUCTIONS:
            1. Carefully analyze the user's correction and determine what specific aspects need to be modified.
            2. Consider these possible correction types:
               - Food identity correction (e.g., "this is chicken, not beef")
               - Ingredient additions/removals/adjustments (e.g., "there's no butter" or "add 15g of cheese")
               - Portion size adjustments (e.g., "this is a half portion")
               - Nutritional value corrections (e.g., "calories should be around 350")
               - Special dietary information (e.g., "this is a vegan version")
            3. Only modify elements that need correction based on the user's feedback.
            4. Keep all other values from the original analysis intact.
            5. Maintain reasonable nutritional consistency (e.g., if calories increase, check if macros need adjustment).
            6. For standard serving size, use common restaurant or cookbook portions for a single adult.
            
            RESPONSE FORMAT:
            Return a valid JSON object with exactly this structure:
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
            
            WARNING CRITERIA:
            - Add "High sodium content" if sodium exceeds 500mg
            - Add "High sugar content" if sugar exceeds 20g
            - Use empty array [] if no warnings apply
            
            IMPORTANT: Return only the JSON object with no additional text, comments, or explanations.
            """
            
            response_text = self.generate_content([prompt])
            return self._parse_food_response(response_text)
        except Exception as e:
            if isinstance(e, GeminiServiceException):
                raise
            raise GeminiServiceException(f"Error correcting food analysis: {str(e)}")
    
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
    
    def _format_food_analysis_result(self, result: FoodAnalysisResult) -> str:
        """
        Format a FoodAnalysisResult for use in prompts.
        
        Args:
            result: The FoodAnalysisResult to format.
            
        Returns:
            A formatted string representation of the result.
        """
        ingredients_format = []
        for ingredient in result.ingredients:
            escaped_name = self._escape_string(ingredient.name)
            ingredients_format.append(f'{{"name":"{escaped_name}","servings":{ingredient.servings}}}')
        ingredients_str = ','.join(ingredients_format)
        
        warnings_format = []
        for warning in result.warnings:
            escaped_warning = self._escape_string(warning)
            warnings_format.append(f'"{escaped_warning}"')
        warnings_str = ','.join(warnings_format)
        
        return f"""
        {{
          "food_name": "{self._escape_string(result.food_name)}",
          "ingredients": [{ingredients_str}],
          "nutrition_info": {{
            "calories": {result.nutrition_info.calories},
            "protein": {result.nutrition_info.protein},
            "carbs": {result.nutrition_info.carbs},
            "fat": {result.nutrition_info.fat},
            "sodium": {result.nutrition_info.sodium},
            "fiber": {result.nutrition_info.fiber},
            "sugar": {result.nutrition_info.sugar}
          }},
          "warnings": [{warnings_str}]
        }}
        """
    
    def _escape_string(self, input_str: str) -> str:
        """
        Escape special characters in strings for JSON.
        
        Args:
            input_str: The input string to escape.
            
        Returns:
            The escaped string.
        """
        return (
            input_str
            .replace('\\', '\\\\')
            .replace('"', '\\"')
            .replace('\n', '\\n')
            .replace('\r', '\\r')
            .replace('\t', '\\t')
        ) 