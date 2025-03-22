"""
Gemini API client for interacting with Google's Gemini LLM.
"""
import google.generativeai as genai
from app.utils.exceptions import GeminiAPIError
import base64


class GeminiClient:
    """
    Client for interacting with the Gemini API.
    """
    
    def __init__(self, api_key, model_name="gemini-pro"):
        """
        Initialize the Gemini client.
        
        Args:
            api_key (str): The API key for the Gemini API
            model_name (str): The model to use (default: gemini-pro)
        """
        self.api_key = api_key
        self.model_name = model_name
        self.configure_model()
        
    def configure_model(self):
        """Configure the Gemini API with the API key."""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            raise GeminiAPIError(f"Failed to configure Gemini API: {str(e)}")
    
    def generate_content(self, prompt):
        """
        Generate content using a text prompt.
        
        Args:
            prompt (str): The text prompt to send to the model
            
        Returns:
            Response: The response from the Gemini API
        """
        try:
            return self.model.generate_content(prompt)
        except Exception as e:
            raise GeminiAPIError(f"Failed to generate content: {str(e)}")
    
    def generate_content_with_image(self, prompt, image_data):
        """
        Generate content using a text prompt and an image.
        
        Args:
            prompt (str): The text prompt to send to the model
            image_data (bytes): The image data
            
        Returns:
            Response: The response from the Gemini API
        """
        try:
            # For multimodal analysis we need the vision model
            if self.model_name != "gemini-pro-vision":
                model = genai.GenerativeModel("gemini-pro-vision")
            else:
                model = self.model
                
            # Prepare the image for Gemini
            image_parts = [
                {
                    "mime_type": "image/jpeg",  # Assuming JPEG, adjust as needed
                    "data": base64.b64encode(image_data).decode('utf-8')
                }
            ]
            
            # Combine text and image in a multimodal prompt
            return model.generate_content([prompt, *image_parts])
        except Exception as e:
            raise GeminiAPIError(f"Failed to generate content with image: {str(e)}") 