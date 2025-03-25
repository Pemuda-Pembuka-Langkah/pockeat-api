"""
Exceptions for the Gemini service.
"""

class GeminiServiceException(Exception):
    """Base exception for all Gemini service errors."""
    
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class GeminiAPIKeyMissingError(GeminiServiceException):
    """Exception raised when the Gemini API key is missing."""
    
    def __init__(self):
        """Initialize the exception."""
        super().__init__("Gemini API key is missing. Please set the GOOGLE_API_KEY environment variable.")


class GeminiAPIError(GeminiServiceException):
    """Exception raised when there's an error with the Gemini API."""
    
    def __init__(self, message="Error making request to Gemini API", status_code=500):
        super().__init__(message, status_code=status_code)


class GeminiModelNotFoundError(GeminiServiceException):
    """Exception raised when the specified Gemini model is not found."""
    
    def __init__(self, model_name):
        message = f"Gemini model '{model_name}' not found"
        super().__init__(message, status_code=404)


class GeminiContentParsingError(GeminiServiceException):
    """Exception raised when there's an error parsing the content from Gemini."""
    
    def __init__(self, message="Failed to parse content from Gemini response"):
        super().__init__(message, status_code=500)


class GeminiQuotaExceededError(GeminiServiceException):
    """Exception raised when the Gemini API quota is exceeded."""
    
    def __init__(self):
        message = "Gemini API quota exceeded. Please try again later."
        super().__init__(message, status_code=429)


class GeminiResponseValidationError(GeminiServiceException):
    """Exception raised when the Gemini response cannot be validated against expected format."""
    
    def __init__(self, message="Failed to validate Gemini response against expected format"):
        super().__init__(message, status_code=500)


class GeminiRequestTimeoutError(GeminiServiceException):
    """Exception raised when a request to Gemini API times out."""
    
    def __init__(self):
        message = "Request to Gemini API timed out. Please try again later."
        super().__init__(message, status_code=504) 