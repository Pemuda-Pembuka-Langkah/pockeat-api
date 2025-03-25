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
from src.services.gemini.food.food_analysis_parser import FoodAnalysisParser


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
            # Create a prompt template with properly escaped JSON
            prompt_template = """
            Analyze this food description: "{description}"
            
            Please analyze the ingredients and nutritional content based on this description.
            If not described, assume a standard serving size and ingredients for 1 person only.
            
            Provide a comprehensive analysis including:
            - The name of the food
            - A complete list of ingredients with servings composition (in grams) from portion estimation or standard serving size.
            - Detailed macronutrition information ONLY of calories, protein, carbs, fat, sodium, fiber, and sugar. No need to display other macro information.
            - Add warnings if the food contains high sodium (>500mg) or high sugar (>20g).
            
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
            """
            
            prompt = PromptTemplate(
                input_variables=["description"],
                template=prompt_template
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
            raise GeminiServiceException(f"Failed to analyze food description: {str(e)}")
    
    async def analyze_by_image(self, image_file) -> FoodAnalysisResult:
        """Analyze a food image.
        
        Args:
            image_file: The image file (file-like object).
            
        Returns:
            The food analysis result.
            
        Raises:
            GeminiServiceException: If the analysis fails.
        """
        try:
            # Read the image bytes
            image_bytes = await self._read_image_bytes(image_file)
            
            # Create message content with properly escaped JSON formatting
            message_text = """
            Analyze this food in the image.
            
            Please analyze the ingredients and nutritional content based on what you can see.
            If not clear, assume a standard serving size and ingredients for 1 person only.
            
            Provide a comprehensive analysis including:
            - The name of the food
            - A complete list of ingredients with servings composition (in grams) from portion estimation or standard serving size.
            - Detailed macronutrition information ONLY of calories, protein, carbs, fat, sodium, fiber, and sugar. No need to display other macro information.
            - Add warnings if the food contains high sodium (>500mg) or high sugar (>20g).
            
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
            raise GeminiServiceException(f"Failed to analyze food image: {str(e)}")
    
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
            image_bytes = await self._read_image_bytes(image_file)
            
            # Create message content with properly escaped JSON formatting
            message_text = f"""
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