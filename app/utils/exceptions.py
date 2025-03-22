"""
Custom exceptions for the application.
"""


class APIError(Exception):
    """Base exception for API errors."""
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class GeminiAPIError(APIError):
    """Exception for Gemini API errors."""
    def __init__(self, message, status_code=500):
        super().__init__(f"Gemini API error: {message}", status_code)


class InvalidJSONResponseError(APIError):
    """Exception for invalid JSON responses."""
    def __init__(self, message):
        super().__init__(f"Invalid JSON response: {message}", 500)


class ValidationError(APIError):
    """Exception for data validation errors."""
    def __init__(self, message):
        super().__init__(f"Validation error: {message}", 400) 