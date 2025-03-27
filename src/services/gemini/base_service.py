"""
Base service for Gemini services using LangChain.
"""

import base64
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.services.gemini.exceptions import GeminiAPIKeyMissingError
import binascii


class BaseLangChainService:
    """Base service for Gemini services using LangChain."""
    
    def __init__(self, text_model_name: str = "models/gemini-1.5-pro", multimodal_model_name: str = "models/gemini-1.5-pro"):
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
            temperature=1
        )
        
        # Create multimodal LLM
        self.multimodal_llm = ChatGoogleGenerativeAI(
            model=self.multimodal_model_name,
            google_api_key=api_key,
            temperature=1
        )
    
    async def _read_image_bytes(self, image_file) -> str:
        """Read the image bytes from a file and return base64 encoding.
        
        Args:
            image_file: The image file (file-like object).
            
        Returns:
            The base64-encoded image bytes.
        """
        try:
            # Read file content without await
            image_content = image_file.read()
            
            # Ensure we have bytes
            if not isinstance(image_content, bytes):
                if isinstance(image_content, str):
                    image_content = image_content.encode('utf-8')
                else:
                    # For other types, try to convert to bytes
                    image_content = bytes(image_content)
            
            # Encode as base64
            b64_bytes = base64.b64encode(image_content)
            b64_string = b64_bytes.decode('utf-8')
            
            # Ensure valid padding
            padding = 4 - (len(b64_string) % 4) if len(b64_string) % 4 else 0
            b64_string = b64_string + ('=' * padding)
            
            # Validate the result by trying to decode it (catch bad encodings)
            try:
                base64.b64decode(b64_string)
            except binascii.Error:
                raise ValueError("Generated invalid base64 string. Check image data.")
            
            return b64_string
        
        except Exception as e:
            print(f"Error in _read_image_bytes: {str(e)}")
            raise ValueError(f"Failed to process image: {str(e)}") 