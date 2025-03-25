"""
Base service for Gemini services using LangChain.
"""

import base64
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.services.gemini.exceptions import GeminiAPIKeyMissingError


class BaseLangChainService:
    """Base service for Gemini services using LangChain."""
    
    def __init__(self, text_model_name: str = "models/gemini-1.5-pro", multimodal_model_name: str = "models/gemini-1.5-pro-vision"):
        """Initialize the service.
        
        Args:
            text_model_name: The name of the text model.
            multimodal_model_name: The name of the multimodal model.
            
        Raises:
            GeminiAPIKeyMissingError: If the API key is not set in environment variables.
        """
        self.text_model_name = text_model_name
        self.multimodal_model_name = multimodal_model_name
        
        # Get API key from environment variables
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise GeminiAPIKeyMissingError()
        
        # Create text LLM
        self.text_llm = ChatGoogleGenerativeAI(
            model=self.text_model_name,
            google_api_key=api_key,
            temperature=0.1
        )
        
        # Create multimodal LLM
        self.multimodal_llm = ChatGoogleGenerativeAI(
            model=self.multimodal_model_name,
            google_api_key=api_key,
            temperature=0.1
        )
    
    async def _read_image_bytes(self, image_file) -> str:
        """Read the image bytes from a file.
        
        Args:
            image_file: The image file (file-like object).
            
        Returns:
            The base64-encoded image bytes.
        """
        # Read the file bytes
        image_content = await image_file.read()
        
        # Encode as base64
        return base64.b64encode(image_content).decode("utf-8") 