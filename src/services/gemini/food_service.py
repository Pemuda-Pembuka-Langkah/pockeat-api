"""
Service for food analysis using LangChain and Gemini.
"""

from typing import Optional
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
import json

from src.models.food_analysis import FoodAnalysisResult
from src.services.gemini.base_service import BaseLangChainService
from src.services.gemini.exceptions import GeminiServiceException
from src.services.gemini.utils.food_parser import FoodAnalysisParser


class FoodAnalysisService(BaseLangChainService):
    """Service for food analysis."""
    
    async def analyze_by_text(self, description: str) -> FoodAnalysisResult:
        """Analyze a food description.
        
        Args:
            description: The food description.
            
        Returns:
            The food analysis result.
            
        Raises:
            GeminiServiceException: If the analysis fails.
        """
        try:
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
            
            # Run the chain - handle the new response format
            result = await runnable.ainvoke({"description": description})
            
            # Parse the result - use the result directly as a string
            text_output = result
            
            # Use the existing parser to create a FoodAnalysisResult
            return FoodAnalysisParser.parse(text_output)
        
        except Exception as e:
            print(f"Food analysis error: {str(e)}")
            
            # Return error response instead of raising exception
            error_data = {
                "error": f"Failed to analyze food: {str(e)}",
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
    
    async def analyze_by_image(self, image_file) -> FoodAnalysisResult:
        """Analyze a food image."""
        try:
            # Check if image file exists
            if not image_file:
                return FoodAnalysisResult.from_dict({
                    "error": "No image file provided",
                    "food_name": "Unknown",
                    "ingredients": [],
                    "nutrition_info": {
                        "calories": 0, "protein": 0, "carbs": 0, "fat": 0,
                        "sodium": 0, "fiber": 0, "sugar": 0
                    },
                    "warnings": []
                })
            
            # Try to read the image bytes with better error handling
            try:
                image_bytes = await self._read_image_bytes(image_file)
            except Exception as e:
                print(f"Image reading error: {str(e)}")
                return FoodAnalysisResult.from_dict({
                    "error": f"Failed to process image: {str(e)}",
                    "food_name": "Unknown",
                    "ingredients": [],
                    "nutrition_info": {
                        "calories": 0, "protein": 0, "carbs": 0, "fat": 0,
                        "sodium": 0, "fiber": 0, "sugar": 0
                    },
                    "warnings": []
                })
            
            # Define message text - this was missing in the previous update!
            message_text = """
            You are a food recognition and nutrition analysis expert. Carefully analyze this image and identify any food or meal present in real life.
            
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
            - Analyze the plating surface of the food and provide a detailed list of likely ingredients with estimated servings composition in grams, estimate based on size and portion to the best of your ability.
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
            
            # Create message with image
            message = HumanMessage(
                content=[
                    {"type": "text", "text": message_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_bytes}"}}
                ]
            )
            
            # Try the Gemini API call with explicit error handling
            try:
                response = await self.multimodal_llm.ainvoke([message])
            except Exception as e:
                print(f"Gemini API error: {str(e)}")
                return FoodAnalysisResult.from_dict({
                    "error": f"Gemini API failed to analyze image: {str(e)}",
                    "food_name": "Unknown",
                    "ingredients": [],
                    "nutrition_info": {
                        "calories": 0, "protein": 0, "carbs": 0, "fat": 0,
                        "sodium": 0, "fiber": 0, "sugar": 0
                    },
                    "warnings": []
                })
            
            # Parse response
            if hasattr(response, 'content'):
                text_output = response.content
            else:
                text_output = str(response)
            
            # Parse using FoodAnalysisParser
            return FoodAnalysisParser.parse(text_output)
            
        except Exception as e:
            print(f"Unexpected error in analyze_by_image: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return FoodAnalysisResult.from_dict({
                "error": f"Failed to analyze food image: {str(e)}",
                "food_name": "Unknown",
                "ingredients": [],
                "nutrition_info": {
                    "calories": 0, "protein": 0, "carbs": 0, "fat": 0,
                    "sodium": 0, "fiber": 0, "sugar": 0
                },
                "warnings": []
            })
    
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
        try:
            # Read the image bytes
            image_bytes = self._read_image_bytes(image_file)
            
            # Create message content
            message_text = f"""
            You are a food recognition and nutrition analysis expert. Carefully analyze this nutrition label image. The user will consume {servings} servings.
            
            Please provide a comprehensive analysis including:
            - The name of the food
            - A complete list of ingredients with servings composition in grams
            - Detailed macronutrition information ONLY of calories, protein, carbs, fat, sodium, fiber, and sugar. No need to display other macro information.
            - Add warnings if the food contains high sodium (>500mg) or high sugar (>20g)
            
            BE VERY THOROUGH. YOU WILL BE FIRED. THE CUSTOMER CAN GET POISONED. BE VERY THOROUGH.
            Return your response as a strict JSON object with this exact format with NO COMMENTS:
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
            
            Remember to multiply all nutritional values by {servings} to account for the user's serving size.
            """
            
            # Create prompt with image
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": message_text
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_bytes}"}
                    }
                ]
            )
            
            # Generate response from multimodal LLM
            response = await self.multimodal_llm.ainvoke([message])
            
            # Parse the result - handle different response formats
            if hasattr(response, 'content'):
                text_output = response.content
            else:
                # Handle different response formats
                text_output = str(response)
            
            # Use the existing parser to create a FoodAnalysisResult
            return FoodAnalysisParser.parse(text_output)
        
        except Exception as e:
            raise GeminiServiceException(f"Failed to analyze nutrition label: {str(e)}")
    
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
        try:
            # Format the previous result as JSON string
            previous_result_json = json.dumps(previous_result.to_dict())
            
            # Create a prompt template with properly escaped JSON
            prompt_template = """
            You are a food nutrition expert tasked with correcting a food analysis based on user feedback.

            ORIGINAL ANALYSIS:
            {previous_result}
            
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
            5. Maintain reasonable nutritional consistency.
            
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
            """
            
            prompt = PromptTemplate(
                input_variables=["previous_result", "user_comment"],
                template=prompt_template
            )
            
            # Use RunnableSequence instead of LLMChain
            runnable = prompt | self.text_llm | StrOutputParser()
            
            # Run the chain
            result = await runnable.ainvoke({
                "previous_result": previous_result_json,
                "user_comment": user_comment
            })
            
            # Parse the result directly as a string
            text_output = result
            
            # Use the existing parser to create a FoodAnalysisResult
            return FoodAnalysisParser.parse(text_output)
        
        except Exception as e:
            raise GeminiServiceException(f"Failed to correct food analysis: {str(e)}") 