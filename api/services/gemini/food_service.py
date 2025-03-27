"""
Food analysis service using Gemini API.
"""

import json
import logging
from typing import Dict, Any, List, Optional

from api.services.gemini.base_service import BaseLangChainService
from api.services.gemini.exceptions import GeminiServiceException, GeminiParsingError, InvalidImageError
from api.services.gemini.utils.json_parser import extract_json_from_text, parse_json_safely
from api.models.food_analysis import FoodAnalysisResult, Ingredient, NutritionInfo
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser

# Configure logger
logger = logging.getLogger(__name__)


class FoodAnalysisService(BaseLangChainService):
    """Food analysis service using Gemini API."""
    
    def __init__(self):
        """Initialize the service."""
        super().__init__()
        logger.info("Initializing FoodAnalysisService")
    
    async def analyze_by_text(self, description: str) -> FoodAnalysisResult:
        """Analyze food from a text description.
        
        Args:
            description: The food description.
            
        Returns:
            The food analysis result.
            
        Raises:
            GeminiServiceException: If the analysis fails.
        """
        logger.info(f"Analyzing food from text: {description[:50]}...")
        
        # Create a prompt template
        prompt = PromptTemplate(
            input_variables=["description"],
            template="""
            You are a food recognition and nutrition analysis expert. Carefully analyze this food description: "{description}"
            
            Please analyze the ingredients and nutritional content based on this description.
            If not described, assume a standard serving size and ingredients for 1 person only.
            FOLLOW MY COMMANDS AND ONLY MY COMMANDS, DONT BE STUPID.

            Provide a comprehensive analysis including:
            - The name of the food
            - A complete list of ingredients with servings composition (in grams) from portion estimation or standard serving size.
            - Detailed macronutrition information ONLY of calories, protein, carbs, fat, sodium, fiber, and sugar. No need to display other macro information.
            - Add warnings if the food contains high sodium (>500mg) or high sugar (>20g).
            

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
            For the warnings array, only allowed to put THIS 2 VALUES:
            - Include "High sodium content" (exact text) if sodium exceeds 500mg
            - Include "High sugar content" (exact text) if sugar exceeds 20g
            If there are no warnings, you can include an empty array [] for warnings.
            
            If you cannot identify the food or analyze it properly, the food cant exist in real life or if the food is not edible use this format:
            {
                "error": "Description of the issue",
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
            } """
        )

        # Use RunnableSequence instead of LLMChain
        runnable = prompt | self.text_llm | StrOutputParser()
        
        try:
            # Invoke the model
            response_text = await runnable.invoke({"description": description})
            logger.debug(f"Received response: {response_text[:100]}...")
            
            # Parse the response
            return self._parse_food_analysis_response(response_text, description)
        except GeminiServiceException:
            # Re-raise GeminiServiceExceptions
            raise
        except Exception as e:
            logger.error(f"Error in analyze_by_text: {str(e)}")
            error_message = f"Failed to analyze food text: {str(e)}"
            
            # Return result with error
            return FoodAnalysisResult(
                food_name="Unknown",
                ingredients=[],
                nutrition_info=NutritionInfo(),
                warnings=[],
                error=error_message
            )
    
    async def analyze_by_image(self, image_file) -> FoodAnalysisResult:
        """Analyze food from an image.
        
        Args:
            image_file: The image file (file-like object).
            
        Returns:
            The food analysis result.
            
        Raises:
            GeminiServiceException: If the analysis fails.
        """
        if not image_file:
            error_message = "No image file provided"
            logger.error(error_message)
            return FoodAnalysisResult(
                food_name="Unknown",
                ingredients=[],
                nutrition_info=NutritionInfo(),
                warnings=[],
                error=error_message
            )
        
        logger.info(f"Analyzing food from image: {getattr(image_file, 'filename', 'unknown')}")
        
        try:
            # Read image bytes
            image_base64 = self._read_image_bytes(image_file)
            
            # Generate the prompt for food image analysis
            prompt = self._generate_food_image_analysis_prompt()
            
            # Invoke the multimodal model
            response_text = await self._invoke_multimodal_model(prompt, image_base64)
            logger.debug(f"Received response: {response_text[:100]}...")
            
            # Parse the response
            return self._parse_food_analysis_response(response_text, "image")
        except InvalidImageError as e:
            # Handle image processing errors
            logger.error(f"Invalid image error: {str(e)}")
            return FoodAnalysisResult(
                food_name="Unknown",
                ingredients=[],
                nutrition_info=NutritionInfo(),
                warnings=[],
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Error in analyze_by_image: {str(e)}")
            error_message = f"Failed to analyze food image: {str(e)}"
            
            # Return result with error
            return FoodAnalysisResult(
                food_name="Unknown",
                ingredients=[],
                nutrition_info=NutritionInfo(),
                warnings=[],
                error=error_message
            )
    
    async def analyze_nutrition_label(self, image_file, servings: float = 1.0) -> FoodAnalysisResult:
        """Analyze a nutrition label image.
        
        Args:
            image_file: The image file (file-like object).
            servings: The number of servings.
            
        Returns:
            The food analysis result.
            
        Raises:
            GeminiServiceException: If the analysis fails.
        """
        if not image_file:
            error_message = "No image file provided"
            logger.error(error_message)
            return FoodAnalysisResult(
                food_name="Nutrition Label",
                ingredients=[],
                nutrition_info=NutritionInfo(),
                warnings=[],
                error=error_message
            )
        
        logger.info(f"Analyzing nutrition label from image: {getattr(image_file, 'filename', 'unknown')}")
        
        try:
            # Read image bytes
            image_base64 = self._read_image_bytes(image_file)
            
            # Generate the prompt for nutrition label analysis
            prompt = self._generate_nutrition_label_prompt(servings)
            
            # Invoke the multimodal model
            response_text = await self._invoke_multimodal_model(prompt, image_base64)
            logger.debug(f"Received response: {response_text[:100]}...")
            
            # Parse the response
            return self._parse_food_analysis_response(response_text, "Nutrition Label")
        except InvalidImageError as e:
            # Handle image processing errors
            logger.error(f"Invalid image error: {str(e)}")
            return FoodAnalysisResult(
                food_name="Nutrition Label",
                ingredients=[],
                nutrition_info=NutritionInfo(),
                warnings=[],
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Error in analyze_nutrition_label: {str(e)}")
            error_message = f"Failed to analyze nutrition label: {str(e)}"
            
            # Return result with error
            return FoodAnalysisResult(
                food_name="Nutrition Label",
                ingredients=[],
                nutrition_info=NutritionInfo(),
                warnings=[],
                error=error_message
            )
    
    async def correct_analysis(self, previous_result: FoodAnalysisResult, user_comment: str) -> FoodAnalysisResult:
        """Correct a previous food analysis based on user feedback.
        
        Args:
            previous_result: The previous food analysis result.
            user_comment: The user's feedback.
            
        Returns:
            The corrected food analysis result.
            
        Raises:
            GeminiServiceException: If the correction fails.
        """
        logger.info(f"Correcting food analysis for {previous_result.food_name} with comment: {user_comment}")
        
        # Convert the previous result to a dict for the prompt
        previous_result_dict = previous_result.dict(exclude={"timestamp", "id"})
        
        # Generate the prompt for correction
        prompt = self._generate_correction_prompt(previous_result_dict, user_comment)
        
        try:
            # Invoke the model
            response_text = await self._invoke_text_model(prompt)
            logger.debug(f"Received correction response: {response_text[:100]}...")
            
            # Parse the response
            corrected_result = self._parse_food_analysis_response(response_text, previous_result.food_name)
            
            # Preserve the original ID
            corrected_result.id = previous_result.id
            
            return corrected_result
        except GeminiServiceException:
            # Re-raise GeminiServiceExceptions
            raise
        except Exception as e:
            logger.error(f"Error in correct_analysis: {str(e)}")
            error_message = f"Failed to correct food analysis: {str(e)}"
            
            # Return original result with error
            previous_result.error = error_message
            return previous_result
    
    def _generate_food_analysis_prompt(self, description: str) -> str:
        """Generate a prompt for food analysis.
        
        Args:
            description: The food description.
            
        Returns:
            The prompt.
        """
        return f"""Analyze the following food description and provide detailed nutritional information. 
Return your response as a JSON object with the following structure:

{{
  "food_name": "Descriptive name of the food",
  "ingredients": [
    {{"name": "Ingredient 1", "servings": 100}},
    {{"name": "Ingredient 2", "servings": 50}}
  ],
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

Food description: {description}

Please estimate nutritional values based on standard serving sizes. For servings, use grams where possible.
Include any dietary warnings in the warnings array (e.g., "High sodium content", "Contains common allergens").
"""
    
    def _generate_food_image_analysis_prompt(self) -> str:
        """Generate a prompt for food image analysis.
        
        Returns:
            The prompt.
        """
        return """Analyze this food image and provide detailed nutritional information.
Return your response as a JSON object with the following structure:

{
  "food_name": "Descriptive name of the food",
  "ingredients": [
    {"name": "Ingredient 1", "servings": 100},
    {"name": "Ingredient 2", "servings": 50}
  ],
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

Please estimate nutritional values based on standard serving sizes. For servings, use grams where possible.
Include any dietary warnings in the warnings array (e.g., "High sodium content", "Contains common allergens").
If the image is not clearly food, indicate this in the food_name and set all nutritional values to 0.
"""
    
    def _generate_nutrition_label_prompt(self, servings: float) -> str:
        """Generate a prompt for nutrition label analysis.
        
        Args:
            servings: The number of servings.
            
        Returns:
            The prompt.
        """
        return f"""Analyze this nutrition label image and extract the nutritional information.
The user is consuming {servings} serving(s) of this food.
Return your response as a JSON object with the following structure:

{{
  "food_name": "Name from the nutrition label",
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

Adjust all nutritional values for {servings} serving(s).
Include any dietary warnings based on the nutritional values (e.g., "High sodium content", "High sugar content").
If the image is not clearly a nutrition label, indicate this in the food_name and set all nutritional values to 0.
"""
    
    def _generate_correction_prompt(self, previous_result: Dict[str, Any], user_comment: str) -> str:
        """Generate a prompt for correction.
        
        Args:
            previous_result: The previous food analysis result as a dictionary.
            user_comment: The user's feedback.
            
        Returns:
            The prompt.
        """
        # Convert the previous result to a formatted JSON string
        previous_result_json = json.dumps(previous_result, indent=2)
        
        return f"""I previously analyzed a food item and provided the following nutritional information:

{previous_result_json}

The user has provided this feedback to correct or improve the analysis:
"{user_comment}"

Please correct the analysis based on this feedback. Return your corrected response as a complete JSON object with the same structure as the original analysis.
"""
    
    def _parse_food_analysis_response(self, response_text: str, default_food_name: str) -> FoodAnalysisResult:
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
            
            # Create and return the result
            result = FoodAnalysisResult(
                food_name=data.get("food_name", default_food_name),
                ingredients=ingredients,
                nutrition_info=nutrition_info,
                warnings=warnings
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