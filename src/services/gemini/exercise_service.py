"""
Service for exercise analysis using LangChain and Gemini.
"""

import json
import re
from typing import Optional, Dict, Any

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
            
            # Create a prompt template without JSON templates in the string
            prompt = PromptTemplate(
                input_variables=["description", "weight_info"],
                template="""
                You are a fitness and exercise analysis expert. Carefully analyze this exercise description: "{description}"
                {weight_info}
                
                Please analyze this exercise and provide:
                - Type of exercise (specific activity name)
                - Calories burned (decimal is fine)
                - Duration in minutes (extract from description or make a reasonable estimate)
                - Intensity level (low, moderate, or high) 
                - MET value (Metabolic Equivalent of Task value)
                
                If weight is not provided, use a standard weight of 70 kg for calculations.
                
                BE VERY THOROUGH. THE USER NEEDS ACCURATE ANALYSIS OF THEIR EXERCISE.
                
                Return your response as a valid JSON object with the following keys:
                - exercise_type (string): specific name of the exercise activity
                - calories_burned (number): estimated calories burned
                - duration_minutes (number): duration in minutes
                - intensity_level (string): low, moderate, or high
                - met_value (number): the MET value
                
                IMPORTANT: Do not include any comments, annotations or notes. Only return valid JSON.
                IMPORTANT: The exercise_type field is required and must be included.
                
                CRITICAL: If the exercise description is ambiguous, invalid, or you cannot determine what exercise is being described, add an "error" key to your response. For example:
                {{
                  "error": "Cannot determine exercise type from the provided description",
                  "exercise_type": "Unknown",
                  "calories_burned": 0,
                  "duration_minutes": 0,
                  "intensity_level": "Not specified",
                  "met_value": 0
                }}
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
            
            # Direct parsing without relying on a separate parser
            data = self._parse_json_response(text_output)
            
            # Add the original description
            data["description"] = description
            
            # Create an ExerciseAnalysisResult from the dictionary
            return ExerciseAnalysisResult.from_dict(data)
            
        except Exception as e:
            print(f"Exercise analysis error: {str(e)}")
            
            # Return error response instead of raising exception
            error_data = {
                "error": f"Failed to analyze exercise: {str(e)}",
                "exercise_type": "Unknown",
                "calories_burned": 0,
                "duration_minutes": 0,
                "intensity_level": "Not specified",
                "met_value": 0.0,
                "description": description if description else ""
            }
            return ExerciseAnalysisResult.from_dict(error_data)
    
    def _parse_json_response(self, text_output: str) -> Dict[str, Any]:
        """Parse JSON response from the text output.
        
        Args:
            text_output: The text output from the model.
            
        Returns:
            The parsed JSON data.
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
            print(f"Raw response from Gemini: {json_str}")
            
            # Clean problematic JSON formatting
            json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
            
            # Parse the JSON - if this fails, it will raise an exception
            data = json.loads(json_str)
            
            # Return the data as is, preserving any error keys from Gemini
            return data
            
        except Exception as e:
            print(f"Failed to parse Gemini response: {str(e)}")
            print(f"Raw response: {text_output}")
            
            # Return error response
            return {
                "error": f"Invalid response from Gemini: {str(e)}",
                "exercise_type": "Unknown",
                "calories_burned": 0,
                "duration_minutes": 0,
                "intensity_level": "Not specified",
                "met_value": 0.0
            }
    
    def _ensure_required_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all required fields are present in the data dictionary.
        
        Args:
            data: The data dictionary.
            
        Returns:
            The data dictionary with all required fields.
        """
        # Define default values for required fields
        defaults = {
            "exercise_type": "Unknown",
            "calories_burned": 0,
            "duration_minutes": 0,
            "intensity_level": "Not specified",
            "met_value": 0.0
        }
        
        # Ensure all keys are normalized (trimmed)
        normalized_data = {}
        for key, value in data.items():
            normalized_key = key.strip()
            normalized_data[normalized_key] = value
        
        # Add default values for missing fields
        for key, default_value in defaults.items():
            if key not in normalized_data:
                print(f"Warning: Missing required field '{key}', adding default value")
                normalized_data[key] = default_value
        
        return normalized_data
    
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
            
            # Create a prompt template without JSON examples
            prompt = PromptTemplate(
                input_variables=["previous_result", "user_comment"],
                template="""
                You are an exercise and fitness expert tasked with correcting an exercise analysis based on user feedback.

                ORIGINAL ANALYSIS:
                {previous_result}
                
                USER CORRECTION: "{user_comment}"
                
                INSTRUCTIONS:
                1. Carefully analyze the user's correction and determine what specific aspects need to be modified.
                2. Consider possible correction types like exercise type correction, duration adjustment, intensity level adjustment, calorie burn adjustment, or MET value correction.
                3. Only modify elements that need correction based on the user's feedback.
                4. Keep all other values from the original analysis intact.
                5. Maintain consistency between the intensity level, MET value, and calories burned.
                
                Return your response as a valid JSON object with the following keys:
                - exercise_type (string): specific name of the exercise
                - calories_burned (number): estimated calories
                - duration_minutes (number): duration in minutes
                - intensity_level (string): low, moderate, or high
                - met_value (number): the MET value
                - correction_applied (string): brief description of what was changed
                
                IMPORTANT: The exercise_type field is required and must be included.
                IMPORTANT: Return only valid JSON with no additional comments.
                
                CRITICAL: If the user's correction is unclear, invalid, contradictory, or cannot be applied, add an "error" key to your response with a descriptive message explaining the issue. For example:
                {{
                  "error": "Cannot apply the requested correction as it is unclear what aspect to modify",
                  "exercise_type": "[keep original value]",
                  "calories_burned": [keep original value],
                  "duration_minutes": [keep original value],
                  "intensity_level": "[keep original value]",
                  "met_value": [keep original value],
                  "correction_applied": "No changes made due to unclear instruction"
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
            
            # Direct parsing without relying on a separate parser
            data = self._parse_json_response(text_output)
            
            # Preserve the original description
            data["description"] = previous_result.description
            
            # Make sure we preserve the ID from the previous result
            return ExerciseAnalysisResult.from_dict(data, id=previous_result.id)
            
        except Exception as e:
            print(f"Exercise correction error: {str(e)}")
            raise GeminiServiceException(f"Failed to correct exercise analysis: {str(e)}") 