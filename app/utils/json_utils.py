"""
JSON utilities for parsing and validating responses from Gemini API.
"""
import json
import re
from jsonschema import validate, ValidationError


def parse_json_response(response_text):
    """
    Parse a JSON response from the Gemini API.
    
    This handles cases where the JSON might be embedded in markdown or other text.
    """
    try:
        # First try to parse the response directly as JSON
        return json.loads(response_text)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find anything that looks like JSON (between curly braces)
        json_match = re.search(r'({[\s\S]*?})', response_text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # If all attempts fail, raise an error
        raise ValueError(f"Could not parse JSON from response: {response_text}")


def validate_json_schema(data, schema):
    """
    Validate that the data matches the expected schema.
    
    Args:
        data: The data to validate
        schema: The JSON schema to validate against
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError:
        return False 