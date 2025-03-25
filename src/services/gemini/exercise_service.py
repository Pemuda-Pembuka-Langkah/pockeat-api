"""
Service for exercise analysis using LangChain and Gemini.
"""

import json
from typing import Optional

from langchain_core.prompts import PromptTemplate
from langchain.chains.llm import LLMChain

from src.models.exercise_analysis import ExerciseAnalysisResult
from src.services.gemini.base_service import BaseLangChainService
from src.services.gemini.exceptions import GeminiServiceException


class ExerciseAnalysisService(BaseLangChainService):
    """Service for exercise analysis."""
    
    async def analyze(self, description: str, user_weight_kg: Optional[float] = None) -> ExerciseAnalysisResult:
        """Analyze an exercise description.
        
        Args:
            description: The exercise description.
            user_weight_kg: The user's weight in kilograms (optional).
            
        Returns:
            The exercise analysis result.
            
        Raises:
            GeminiServiceException: If the analysis fails.
        """
        try:
            # Add weight info if provided
            weight_info = f"The user weighs {user_weight_kg} kg." if user_weight_kg else ""
            
            # Create a prompt template
            prompt = PromptTemplate(
                input_variables=["description", "weight_info"],
                template="""
                Calculate calories burned from this exercise description: "{description}"
                {weight_info}
                
                Please analyze this exercise and provide:
                - Type of exercise (specific activity name)
                - Calories burned (decimal is fine)
                - Duration in minutes (extract from description or make a reasonable estimate)
                - Intensity level (low, moderate, or high) 
                - MET value (Metabolic Equivalent of Task value)
                
                If weight is not provided, use a standard weight of 70 kg for calculations.
                
                Return your response as a strict JSON object with this exact format with NO COMMENTS:
                {
                  "exercise_type": "string",
                  "calories_burned": number,
                  "duration_minutes": number,
                  "intensity_level": "string",
                  "met_value": number
                }
                """
            )
            
            # Create a chain
            chain = LLMChain(llm=self.text_llm, prompt=prompt)
            
            # Run the chain
            result = await chain.ainvoke({
                "description": description,
                "weight_info": weight_info
            })
            
            # Parse the result - handle different output formats
            if "text" in result:
                text_output = result["text"]
            else:
                # In newer versions, the output might be directly in the 'content' field
                # or in the 'output' field depending on the LangChain version
                text_output = result.get("content", result.get("output", str(result)))
            
            # Parse JSON from the text
            try:
                # Try to extract JSON from the text
                import re
                json_match = re.search(r'({.*})', text_output, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = text_output
                
                # Parse the JSON
                data = json.loads(json_str)
                
                # Add the original description
                data["description"] = description
                
                # Create an ExerciseAnalysisResult from the dictionary
                return ExerciseAnalysisResult.from_dict(data)
            
            except Exception as e:
                raise GeminiServiceException(f"Failed to parse exercise analysis result: {str(e)}")
        
        except Exception as e:
            raise GeminiServiceException(f"Failed to analyze exercise description: {str(e)}")
    
    async def correct_analysis(self, previous_result: ExerciseAnalysisResult, user_comment: str) -> ExerciseAnalysisResult:
        """Correct a previous exercise analysis based on user feedback.
        
        Args:
            previous_result: The previous exercise analysis result.
            user_comment: The user's feedback.
            
        Returns:
            The corrected exercise analysis result.
            
        Raises:
            GeminiServiceException: If the correction fails.
        """
        try:
            # Format the previous result as JSON string
            previous_result_json = json.dumps(previous_result.to_dict())
            
            # Create a prompt template
            prompt = PromptTemplate(
                input_variables=["previous_result", "user_comment"],
                template="""
                You are an exercise and fitness expert tasked with correcting an exercise analysis based on user feedback.

                ORIGINAL ANALYSIS:
                {previous_result}
                
                USER CORRECTION: "{user_comment}"
                
                INSTRUCTIONS:
                1. Carefully analyze the user's correction and determine what specific aspects need to be modified.
                2. Consider these possible correction types:
                   - Exercise type correction (e.g., "this was running, not jogging")
                   - Duration adjustment (e.g., "I exercised for 45 minutes, not 30")
                   - Intensity level adjustment (e.g., "this was high intensity, not moderate")
                   - Calorie burn adjustment (e.g., "I think I burned about 400 calories")
                   - MET value correction (e.g., "the MET value for walking should be lower")
                3. Only modify elements that need correction based on the user's feedback.
                4. Keep all other values from the original analysis intact.
                5. Maintain consistency between the intensity level, MET value, and calories burned.
                
                Return your response as a strict JSON object with this exact format:
                {{
                  "exercise_type": "string",
                  "calories_burned": number,
                  "duration_minutes": number,
                  "intensity_level": "string",
                  "met_value": number,
                  "description": "string"
                }}
                """
            )
            
            # Create a chain
            chain = LLMChain(llm=self.text_llm, prompt=prompt)
            
            # Run the chain
            result = await chain.ainvoke({
                "previous_result": previous_result_json,
                "user_comment": user_comment
            })
            
            # Parse the result - handle different output formats
            if "text" in result:
                text_output = result["text"]
            else:
                # In newer versions, the output might be directly in the 'content' field
                # or in the 'output' field depending on the LangChain version
                text_output = result.get("content", result.get("output", str(result)))
            
            # Parse JSON from the text
            try:
                # Try to extract JSON from the text
                import re
                json_match = re.search(r'({.*})', text_output, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = text_output
                
                # Parse the JSON
                data = json.loads(json_str)
                
                # Make sure we preserve the ID from the previous result
                return ExerciseAnalysisResult.from_dict(data, id=previous_result.id)
            
            except Exception as e:
                raise GeminiServiceException(f"Failed to parse corrected exercise analysis result: {str(e)}")
        
        except Exception as e:
            raise GeminiServiceException(f"Failed to correct exercise analysis: {str(e)}") 