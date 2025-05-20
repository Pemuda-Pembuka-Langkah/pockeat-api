"""
Food analysis service using Gemini API.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Tuple

from supabase import create_client, Client
from langchain.prompts import PromptTemplate
from api.services.gemini.base_service import BaseLangChainService
from api.services.gemini.exceptions import (
    GeminiServiceException,
    InvalidImageError,
)
from api.services.gemini.utils.json_parser import (
    extract_json_from_text,
    parse_json_safely,
)
from api.models.food_analysis import FoodAnalysisResult, Ingredient, NutritionInfo
from langchain.prompts import PromptTemplate

# Configure logger
logger = logging.getLogger(__name__)

class FoodAnalysisService(BaseLangChainService):
    """Food analysis service using Gemini API."""

    # Constants for thresholds (kept for documentation purposes)
    HIGH_SODIUM_THRESHOLD = 500  # mg
    HIGH_SUGAR_THRESHOLD = 20.0  # g
    HIGH_CHOLESTEROL_THRESHOLD = 200.0  # mg
    HIGH_SATURATED_FAT_THRESHOLD = 5.0  # g

    def __init__(self):
        super().__init__()
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase URL or Key not found in environment variables. RAG will be disabled.")
            self.supabase_client: Optional[Client] = None
        else:
            self.supabase_client: Client = create_client(self.supabase_url, self.supabase_key)

    async def _retrieve_relevant_food_data(self, query: str) -> Tuple[List[Dict[str, Any]], str]:
        """Retrieve relevant food records from Supabase and generate context for RAG."""
        if not self.supabase_client:
            logger.warning("Supabase client not initialized, skipping RAG retrieval.")
            return [], ""

        try:
            # Step 1: Ekstrak nama makanan dari input user pakai Gemini
            extracted_food = await self._extract_food_names_with_gemini(query)
            if not extracted_food:
                return [], ""

            # Step 2: Ambil data nutrisi dari Supabase
            cleaned_data = []
            context_lines = ["\n\nRelevant Nutrition Facts From Local DB:\n"]

            for food_name in extracted_food:
                response = self.supabase_client.table("nutrition_data") \
                    .select("*") \
                    .ilike("food", f"%{food_name}%") \
                    .limit(1) \
                    .execute()

                if response.data:
                    entry = response.data[0]

                    # Build cleaned data
                    nutrition_info = {
                        "calories": entry.get("caloric_value", 0.0),
                        "protein": entry.get("protein", 0.0),
                        "carbs": entry.get("carbohydrates", 0.0),
                        "fat": entry.get("fat", 0.0),
                        "saturated_fat": entry.get("saturated_fats", 0.0),
                        "sodium": entry.get("sodium", 0.0),
                        "fiber": entry.get("dietary_fiber", 0.0),
                        "sugar": entry.get("sugars", 0.0),
                        "cholesterol": entry.get("cholesterol", 0.0),
                        "nutrition_density": entry.get("nutrition_density", 0.0),
                        "vitamins_and_minerals": {
                            "vitamin_a": entry.get("vitamin_a", 0.0),
                            "vitamin_b1": entry.get("vitamin_b1", 0.0),
                            "vitamin_b11": entry.get("vitamin_b11", 0.0),
                            "vitamin_b12": entry.get("vitamin_b12", 0.0),
                            "vitamin_b2": entry.get("vitamin_b2", 0.0),
                            "vitamin_b3": entry.get("vitamin_b3", 0.0),
                            "vitamin_b5": entry.get("vitamin_b5", 0.0),
                            "vitamin_b6": entry.get("vitamin_b6", 0.0),
                            "vitamin_c": entry.get("vitamin_c", 0.0),
                            "vitamin_d": entry.get("vitamin_d", 0.0),
                            "vitamin_e": entry.get("vitamin_e", 0.0),
                            "vitamin_k": entry.get("vitamin_k", 0.0),
                            "calcium": entry.get("calcium", 0.0),
                            "copper": entry.get("copper", 0.0),
                            "iron": entry.get("iron", 0.0),
                            "magnesium": entry.get("magnesium", 0.0),
                            "manganese": entry.get("manganese", 0.0),
                            "phosphorus": entry.get("phosphorus", 0.0),
                            "potassium": entry.get("potassium", 0.0),
                            "selenium": entry.get("selenium", 0.0),
                            "zinc": entry.get("zinc", 0.0)
                        }
                    }

                    cleaned_data.append({
                        "food_name": entry["food"],
                        "nutrition_info": nutrition_info
                    })

                    # Add to RAG context
                    context_lines.append(f"- Food: {entry['food']}")
                    for k, v in nutrition_info.items():
                        if k == "vitamins_and_minerals":
                            context_lines.append("  Vitamins and minerals:")
                            for vk, vv in v.items():
                                context_lines.append(f"    - {vk}: {vv}")
                        else:
                            context_lines.append(f"  {k.replace('_', ' ').capitalize()}: {v}")
                    context_lines.append("")

            context_str = "\n".join(context_lines)
            return cleaned_data, context_str

        except Exception as e:
            logger.error(f"Failed to retrieve relevant food data: {str(e)}")
            return [], ""


    async def analyze_by_text(self, description: str) -> FoodAnalysisResult:
        """Analyze food from a text description, using RAG if relevant data exists.

        Args:
            description: The food description.

        Returns:
            The food analysis result.
        """

        # Step 1: Try to retrieve context from Supabase
        _, context = await self._retrieve_relevant_food_data(description)
        # Step 2: Inject description and context into prompt
        try:
            prompt_text = self._generate_food_text_analysis_prompt(description=description, context=context)
            prompt = PromptTemplate(input_variables=["description", "context"], template=prompt_text)
            formatted_prompt = prompt.format(description=description, context=context)

            # Step 3: Call Gemini model
            response_text = await self._invoke_text_model(formatted_prompt)

            # Step 4: Parse result
            return self._parse_food_analysis_response(response_text, default_food_name=description)
        except GeminiServiceException:
            raise
        except Exception as e:
            logger.error(f"Error in analyze_by_text with RAG: {str(e)}")
            return FoodAnalysisResult(
                food_name="Unknown",
                ingredients=[],
                nutrition_info=NutritionInfo(),
                error=f"Failed to analyze food text: {str(e)}"
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
                error=error_message,
            )

        try:
            # Read image bytes
            image_base64 = self._read_image_bytes(image_file)

            # Generate the prompt for food image analysis
            prompt = self._generate_food_image_analysis_prompt()

            # Invoke the multimodal model
            response_text = await self._invoke_multimodal_model(prompt, image_base64)

            # Parse the response
            return self._parse_food_analysis_response(response_text, "image")
        except InvalidImageError as e:
            # Handle image processing errors
            logger.error(f"Invalid image error: {str(e)}")
            return FoodAnalysisResult(
                food_name="Unknown",
                ingredients=[],
                nutrition_info=NutritionInfo(),
                error=str(e),
            )
        except Exception as e:  # pragma: no cover
            logger.error(f"Error in analyze_by_image: {str(e)}")
            error_message = f"Failed to analyze food image: {str(e)}"

            # Return result with error
            return FoodAnalysisResult(
                food_name="Unknown",
                ingredients=[],
                nutrition_info=NutritionInfo(),
                error=error_message,
            )

    async def analyze_nutrition_label(
        self, image_file, servings: float = 1.0
    ) -> FoodAnalysisResult:
        """Analyze a nutrition label image.

        Args:
            image_file: The image file (file-like object).
            servings: The number of servings.

        Returns:
            The food analysis result.

        Raises:
            GeminiServiceException: If the analysis fails.
        """
        if not image_file:  # pragma: no cover
            error_message = "No image file provided"
            logger.error(error_message)
            return FoodAnalysisResult(
                food_name="Nutrition Label",
                ingredients=[],
                nutrition_info=NutritionInfo(),
                error=error_message,
            )   
        try:
            # Read image bytes
            image_base64 = self._read_image_bytes(image_file)

            # Generate the prompt for nutrition label analysis
            prompt = self._generate_nutrition_label_prompt(servings)

            # Invoke the multimodal model
            response_text = await self._invoke_multimodal_model(prompt, image_base64)

            # Parse the response
            return self._parse_food_analysis_response(response_text, "Nutrition Label")
        except InvalidImageError as e:
            # Handle image processing errors
            logger.error(f"Invalid image error: {str(e)}")  # pragma: no cover
            return FoodAnalysisResult(  # pragma: no cover
                food_name="Nutrition Label",
                ingredients=[],
                nutrition_info=NutritionInfo(),
                error=str(e),
            )
        except Exception as e:  # pragma: no cover
            logger.error(f"Error in analyze_nutrition_label: {str(e)}")
            error_message = f"Failed to analyze nutrition label: {str(e)}"

            # Return result with error
            return FoodAnalysisResult(
                food_name="Nutrition Label",
                ingredients=[],
                nutrition_info=NutritionInfo(),
                error=error_message,
            )

    async def correct_analysis(
        self, previous_result: FoodAnalysisResult, user_comment: str
    ) -> FoodAnalysisResult:
        """Correct a previous food analysis based on user feedback.

        Args:
            previous_result: The previous food analysis result.
            user_comment: The user's feedback.

        Returns:
            The corrected food analysis result.

        Raises:
            GeminiServiceException: If the correction fails.
        """

        # Convert the previous result to a dict for the prompt
        previous_result_dict = previous_result.dict(exclude={"timestamp", "id"})

        # Generate the prompt for correction
        prompt = self._generate_correction_prompt(previous_result_dict, user_comment)

        try:
            # Invoke the model
            response_text = await self._invoke_text_model(prompt)

            # Parse the response
            corrected_result = self._parse_food_analysis_response(
                response_text, previous_result.food_name
            )

            # Preserve the original ID
            corrected_result.id = previous_result.id

            return corrected_result
        except GeminiServiceException:
            # Re-raise GeminiServiceExceptions
            raise
        except Exception as e:  # pragma: no cover
            logger.error(f"Error in correct_analysis: {str(e)}")
            error_message = f"Failed to correct food analysis: {str(e)}"

            # Return original result with error
            previous_result.error = error_message
            return previous_result

    def _generate_food_text_analysis_prompt(self, description: str, context: str = "") -> str:
        """Generate a prompt for food analysis.

        Args:
            description: The food description.

        Returns:
            The prompt.
        """
        return f"""
            You are a food recognition and nutrition analysis expert. Carefully analyze this food description: {description}{context}
            
            Please analyze the ingredients and nutritional content based on this description.
            If not described, assume a standard serving size and ingredients for 1 person only.

            If you were provided a nutrition context, you MUST use the nutrition values from that context.
            You are allowed to generate nutrition information if the context does not contain an exact or close enough match.
            Only use nutrition context from DB if it clearly matches the described food item.
            Otherwise, use your expert knowledge to estimate it accurately.
            
            Provide a comprehensive analysis including:
            - The name of the food
            - A complete list of ingredients with servings composition (in kcal) from portion estimation or standard serving size.
            - Detailed nutrition information including:
              * Calories (in kcal)
              * Protein (in g)
              * Carbs (in g)
              * Fat (in g)
              * Saturated fat (in g)
              * Sodium (in mg)
              * Fiber (in g)
              * Sugar (in g)
              * Cholesterol (in mg)
            - Calculate a nutrition density score based on nutrient richness per calorie (using a formula that considers protein, fiber, vitamins, minerals, and deducts for saturated fat, sodium, and sugar)
            - Include any important vitamins and minerals with their values in mg
            
            BE VERY THOROUGH. YOU WILL BE FIRED. THE CUSTOMER CAN GET POISONED. BE VERY THOROUGH.
            REMEMBER. If not described, assume a standard serving size and ingredients for 1 person only.

            Return your response as a strict JSON object with this exact format with NO COMMENTS:
            {{{{
                "food_name": "string",
                "ingredients": [
                {{{{
                    "name": "string",
                    "servings": number in kcal
                }}}}
                ],
                "nutrition_info": {{{{
                "calories": number in kcal,
                "protein": number in grams,
                "carbs": number in grams,
                "fat": number in grams,
                "saturated_fat": number in grams,
                "sodium": number in miligrams,
                "fiber": number in grams,
                "sugar": number in grams,
                "cholesterol": number in mg,
                "nutrition_density": number from calculation,
                "vitamins_and_minerals": {{{{
                    "vitamin_a": number,
                    "vitamin_c": number,
                    [other vitamins and minerals as detected] in miligrams
                }}}}
                }}}}
            }}}}
            ONLY return valid, parsable JSON. Do NOT include markdown ```json wrappers, comments, or extra explanations.
            Make sure the JSON is valid and parsable. Do not include any comments, annotations or notes in the JSON.

            IMPORTANT: Do not return a list. Return a single JSON object with the specified keys.
            IMPORTANT: Do not include any comments, annotations or notes in the JSON. Do not use '#' or '//' characters. Only return valid JSON.
            Make sure the ingredients's servings (kcal) adds up to the food kcal itself.
            If you cannot identify the food or analyze it properly, the food cant exist in real life or if the food is not edible use this format:
            {{{{
                "error": "Description of the issue",
                "food_name": "Unknown",
                "ingredients": [],
                "nutrition_info": {{{{
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0,
                "saturated_fat": 0,
                "sodium": 0,
                "fiber": 0,
                "sugar": 0,
                "cholesterol": 0,
                "nutrition_density": 0,
                "vitamins_and_minerals": {{{{}}}}
                }}}}
            }}}}"""

    def _generate_food_image_analysis_prompt(self) -> str:
        """Generate a prompt for food image analysis.

        Returns:
            The prompt.
        """
        return """
            You are a food recognition and nutrition analysis expert. Carefully analyze this image and identify any food or meal present.

            Please look for:
            - Prepared meals
            - Individual food items
            - Snacks
            - Beverages
            - Fruits and vegetables
            - Packaged food products

            Even if the image quality is not perfect or the food is partially visible, please do your best to identify it and provide an analysis.

            For the identified food, provide a comprehensive analysis including:
            - The specific name of the food
            - A detailed list of likely ingredients with estimated servings composition in calories
            - Detailed nutrition information including:
              * Calories (in kcal)
              * Protein (in g)
              * Carbs (in g)
              * Fat (in g)
              * Saturated fat (in g)
              * Sodium (in mg)
              * Fiber (in g)
              * Sugar (in g)
              * Cholesterol (in mg)
            - Calculate a nutrition density score from 0-100 based on nutrient richness per calorie
            - Include any important vitamins and minerals with their values

            Return your response as a JSON object with the following structure:

            {{{{
              "food_name": "Descriptive name of the food",
              "ingredients": [
                {{"name": "Ingredient 1", "servings": 100 in kcal}},
                {{"name": "Ingredient 2", "servings": 50 in kcal}}
              ],
              "nutrition_info": {{{{
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0,
                "saturated_fat": 0,
                "sodium": 0,
                "fiber": 0,
                "sugar": 0,
                "cholesterol": 0,
                "nutrition_density": 0,
                "vitamins_and_minerals": {{{{
                  "vitamin_a": 0,
                  "vitamin_c": 0
                }}}}
              }}}}
            }}}}
            Make sure the ingredients's servings (kcal) adds up to the food kcal itself.

            If the image is not clearly food, indicate this in the food_name (Unknown) and set all nutritional values to 0.
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

            Make sure calories is in kcal and extract all nutritional information you can find:
            - Calories (in kcal)
            - Protein (in g)
            - Carbs (in g)
            - Fat (in g)
            - Saturated fat (in g)
            - Sodium (in mg)
            - Fiber (in g)
            - Sugar (in g)
            - Cholesterol (in mg)
            - All vitamins and minerals with their values
            
            Also calculate a nutrition density score based on how nutrient-rich this food is per calorie.

            Return your response as a JSON object with the following structure:

            {{{{
              "food_name": "Name from the nutrition label",
              "ingredients": [],
              "nutrition_info": {{{{
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0,
                "saturated_fat": 0,
                "sodium": 0,
                "fiber": 0,
                "sugar": 0,
                "cholesterol": 0,
                "nutrition_density": 0,
                "vitamins_and_minerals": {{{{
                  "vitamin_a": 0,
                  "vitamin_c": 0,
                  "calcium": 0,
                  "iron": 0,
                  [other vitamins and minerals as detected]
                }}}}
              }}}}
            }}}}

            Adjust all nutritional values for {servings} serving(s).
            If the image is not clearly a nutrition label, indicate this in the food_name (Unknown) and set all nutritional values to 0.
            """

    def _generate_correction_prompt(
        self, previous_result: Dict[str, Any], user_comment: str
    ) -> str:
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

            Please understand the context of the user's feedback for analysis, if the user feedback is not clear, just return previous result as is.
            Make sure ingredient servings and calories in kcal and macros in grams.
            Please correct the analysis based on this feedback. Return your corrected response as a complete JSON object with the same structure as the original analysis.

            The response should include all the fields shown in the original analysis. Make sure to preserve any existing fields for:
            - calories, protein, carbs, fat, saturated_fat, sodium, fiber, sugar, cholesterol, nutrition_density
            - Any vitamins_and_minerals that were included before
            
            If the user is providing information about a field that wasn't in the original analysis, add that field to the response.
            
            Your response should be in this format:
            {{{{
              "food_name": "Corrected name of the food",
              "ingredients": [
                {{{{
                  "name": "Ingredient name",
                  "servings": number
                }}}}
              ],
              "nutrition_info": {{{{
                "calories": number,
                "protein": number,
                "carbs": number,
                "fat": number,
                "saturated_fat": number,
                "sodium": number,
                "fiber": number,
                "sugar": number,
                "cholesterol": number,
                "nutrition_density": number,
                "vitamins_and_minerals": {{{{
                  "vitamin_a": number,
                  "vitamin_c": number,
                  [other vitamins and minerals as detected]
                }}}}
              }}}}
            }}}}

    
            
            If correction doesnt make sense, return previous json result with the error message in error attribute in json and unknown food name.
            NOTHING ELSE IS ALLOWED, ONLY VALID JSON RESPONSE. EXPLANATION OF CHANGES IS NOT NEEDED!
            """

    def _parse_food_analysis_response(
        self, response_text: str, default_food_name: str
    ) -> FoodAnalysisResult:
        """Parse the response from the Gemini API for food analysis.

        Args:
            response_text: The response text from the Gemini API.
            default_food_name: Default food name to use if parsing fails.

        Returns:
            The food analysis result.
        """
        try:
            # Remove markdown code block if present
            response_text = response_text.strip()

            # Decode if it's in bytes and sanitize
            if isinstance(response_text, bytes):
                response_text = response_text.decode("utf-8", errors="replace")

            # Replace known weird artifacts
            response_text = response_text.replace('\ufeff', '')  # BOM
            response_text = response_text.replace('<?xml version="1.0" encoding="UTF-8"?>', '')  # common header


            # Remove any markdown code fence regardless of language
            if response_text.startswith("```"):
                response_text = response_text.split("```", 1)[-1].strip()
            if response_text.endswith("```"):
                response_text = response_text.rsplit("```", 1)[0].strip()

            # Also remove weird XML-like headers
            if response_text.startswith("<?"):
                response_text = response_text.split("?>", 1)[-1].strip()
            
            # If it starts with 'json\n{', strip that broken markdown hint
            if response_text.lower().startswith("json\n"):
                response_text = response_text[5:].lstrip()

            # Extract JSON from the response
            json_str = extract_json_from_text(response_text)
            if not json_str:
                logger.warning("No JSON found in response, returning raw response")
                return self._create_error_result(
                    default_food_name,
                    f"Failed to parse response: {response_text[:100]}...",
                )

            # Parse the JSON
            data = parse_json_safely(json_str)

            # Extract ingredients
            ingredients = self._extract_ingredients(data)

            # Extract nutrition info
            nutrition_info = self._extract_nutrition_info(data)

            # Create and return the result
            result = FoodAnalysisResult(
                food_name=data.get("food_name", default_food_name),  # pragma: no cover
                ingredients=ingredients,
                nutrition_info=nutrition_info,
                error=data.get("error"),
            )

            return result

        except Exception as e:
            logger.error(
                f"Error parsing food analysis response: {str(e)}"
            )  # pragma: no cover
            # Instead of raising an exception, return a result with the error
            return FoodAnalysisResult(  # pragma: no cover
                food_name=default_food_name,
                ingredients=[],
                nutrition_info=NutritionInfo(),
                error=f"Failed to parse response: {str(e)}",
            )

    # Remove the _generate_warnings method as warnings are handled in the Flutter model

    def _extract_ingredients(self, data: Dict[str, Any]) -> List[Ingredient]:
        """Extract ingredients from parsed data.

        Args:
            data: The parsed JSON data.

        Returns:
            List of ingredients.
        """
        ingredients = []
        if "ingredients" in data and isinstance(data["ingredients"], list):
            for ing_data in data["ingredients"]:
                if isinstance(ing_data, dict):  # pragma: no cover
                    name = ing_data.get("name", "Unknown ingredient")
                    servings = float(ing_data.get("servings", 0))
                    ingredients.append(Ingredient(name=name, servings=servings))
        return ingredients

    def _extract_nutrition_info(self, data: Dict[str, Any]) -> NutritionInfo:
        """Extract nutrition info from parsed data.

        Args:
            data: The parsed JSON data.

        Returns:
            Nutrition info object.
        """
        nutrition_info = NutritionInfo()
        if "nutrition_info" in data and isinstance(data["nutrition_info"], dict):
            nutrition_data = data["nutrition_info"]
            
            # Extract vitamins and minerals if present
            vitamins_and_minerals = {}
            if "vitamins_and_minerals" in nutrition_data and isinstance(nutrition_data["vitamins_and_minerals"], dict):
                for key, value in nutrition_data["vitamins_and_minerals"].items():
                    try:
                        vitamins_and_minerals[key] = float(value)
                    except (ValueError, TypeError):
                        logger.warning(f"Could not convert {key} value to float: {value}")
            
            # Create nutrition info object with all fields
            nutrition_info = NutritionInfo(
                calories=float(nutrition_data.get("calories", 0)),
                protein=float(nutrition_data.get("protein", 0)),
                carbs=float(nutrition_data.get("carbs", 0)),
                fat=float(nutrition_data.get("fat", 0)),
                saturated_fat=float(nutrition_data.get("saturated_fat", 0)),
                sodium=float(nutrition_data.get("sodium", 0)),
                fiber=float(nutrition_data.get("fiber", 0)),
                sugar=float(nutrition_data.get("sugar", 0)),
                cholesterol=float(nutrition_data.get("cholesterol", 0)),
                nutrition_density=float(nutrition_data.get("nutrition_density", 0)),
                vitamins_and_minerals=vitamins_and_minerals
            )
        return nutrition_info

    def _create_error_result(
        self, food_name: str, error_message: str
    ) -> FoodAnalysisResult:
        """Create an error result.

        Args:
            food_name: The food name.
            error_message: The error message.

        Returns:
            Food analysis result with error.
        """
        return FoodAnalysisResult(
            food_name=food_name,
            ingredients=[],
            nutrition_info=NutritionInfo(),
            error=error_message,
        )
    
    async def _extract_food_names_with_gemini(self, description: str) -> List[str]:
        """Use Gemini to extract food names from a long user description."""
        prompt = f"""
    You are an expert in Indonesian food recognition.

    From the following user input, extract a list of clearly named food or drink items mentioned.
    Respond with only a valid JSON list. Do not include any other text.

    Input:
    "{description}"

    Output format:
    ["food name 1", "food name 2", "..."]
    """
        try:
            response = await self._invoke_text_model(prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Failed to extract food names: {e}")
            return []
