import os
import re
import json
import google.generativeai as genai
from flask import current_app
from typing import List, Dict, Any, Union


class GeminiServiceException(Exception):
    """Exception raised for errors in the Gemini service."""
    pass


class BaseGeminiService:
    """Base service for interacting with Google's Gemini API."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Gemini service.
        
        Args:
            api_key: The Gemini API key. If not provided, it will attempt to get from environment variables.
        """
        self.api_key = api_key or self._get_api_key_from_env()
        genai.configure(api_key=self.api_key)
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Gemini model."""
        model_name = 'gemini-1.5-pro'
        generation_config = {
            "temperature": 1,
            "top_k": 40,
            "top_p": 0.95,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )
    
    def _get_api_key_from_env(self) -> str:
        """
        Get the Gemini API key from environment variables.
        
        Returns:
            The Gemini API key.
        
        Raises:
            GeminiServiceException: If the API key is not found.
        """
        api_key = os.environ.get('GEMINI_API_KEY') or current_app.config.get('GEMINI_API_KEY')
        if not api_key:
            raise GeminiServiceException('GEMINI_API_KEY not found in environment variables')
        return api_key
    
    def generate_content(self, contents: List[Union[str, Dict[str, Any]]]) -> str:
        """
        Generate content using Gemini API.
        
        Args:
            contents: The list of content parts to send to Gemini.
            
        Returns:
            The generated text response.
            
        Raises:
            GeminiServiceException: If there's an error generating content.
        """
        try:
            response = self.model.generate_content(contents)
            if not response.text:
                raise GeminiServiceException('No response text generated')
            return response.text
        except Exception as e:
            raise GeminiServiceException(f"Error generating content: {str(e)}")
    
    def extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from a text response.
        
        Args:
            text: The text containing JSON.
            
        Returns:
            The extracted JSON as a dictionary.
            
        Raises:
            GeminiServiceException: If JSON extraction fails.
        """
        try:
            # First, try to parse directly assuming it's clean JSON
            text = self._clean_json_text(text)
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON from within text
                start_index = text.find('{')
                end_index = text.rfind('}')
                
                if start_index >= 0 and end_index >= 0 and end_index > start_index:
                    json_string = text[start_index:end_index + 1]
                    json_string = self._clean_json_text(json_string)
                    
                    try:
                        return json.loads(json_string)
                    except json.JSONDecodeError as e:
                        raise GeminiServiceException(f'Extracted text is not valid JSON: {e}')
                
                raise GeminiServiceException('No valid JSON found in response')
        except Exception as e:
            if isinstance(e, GeminiServiceException):
                raise
            raise GeminiServiceException(f'Error extracting JSON: {e}')

    def _clean_json_text(self, text: str) -> str:
        """
        Clean JSON text by removing comments and fixing common issues.
        
        Args:
            text: The JSON text to clean.
            
        Returns:
            Cleaned JSON text.
        """
        # Remove JavaScript-style comments (both // and /* */)
        cleaned = re.sub(r'//.*?(\n|$)', '', text)
        cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)
        
        # Remove trailing commas in arrays and objects
        cleaned = re.sub(r',\s*}', '}', cleaned)
        cleaned = re.sub(r',\s*\]', ']', cleaned)
        
        # Replace single quotes with double quotes for JSON compliance
        parts = []
        in_quotes = False
        in_single_quotes = False
        
        i = 0
        while i < len(cleaned):
            char = cleaned[i]
            
            if char == '"' and (i == 0 or cleaned[i - 1] != '\\'):
                in_quotes = not in_quotes
            elif char == "'" and (i == 0 or cleaned[i - 1] != '\\') and not in_quotes:
                in_single_quotes = not in_single_quotes
                char = '"'  # Replace single quote with double quote
            
            parts.append(char)
            i += 1
        
        cleaned = ''.join(parts)
        return cleaned 