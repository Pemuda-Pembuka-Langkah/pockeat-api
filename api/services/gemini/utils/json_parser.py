"""
JSON parsing utilities for Gemini API responses.
"""

import json
import re
import logging
from typing import Dict, Any, Optional, List, Tuple

from api.services.gemini.exceptions import GeminiParsingError

# Configure logger
logger = logging.getLogger(__name__)


def extract_json_from_text(text: str) -> Optional[str]:
    """Extract JSON from text response.
    
    This function handles various formats where JSON might be embedded in text,
    including Markdown code blocks and irregular JSON formatting.
    
    Args:
        text: The text response from the Gemini API.
        
    Returns:
        The extracted JSON string, or None if no JSON was found.
    """
    # Log the input for debugging
    logger.debug(f"Extracting JSON from text: {text[:100]}...")  # pragma: no cover
    
    # Try to extract JSON from markdown code blocks
    # Using a more efficient regex with atomic groups to prevent catastrophic backtracking
    json_block_pattern = r"```(?:json)?(?>((?:(?!```).)*))```"
    matches = re.findall(json_block_pattern, text, re.DOTALL)
    
    if matches:
        # If we found JSON blocks, use the first one
        return matches[0].strip()
    
    # If no code blocks found, look for JSON objects or arrays
    # Using a safer pattern that avoids backtracking issues
    try:
        # Look for objects
        json_obj_pattern = r"({(?:[^{}]|(?R))*})"
        match_obj = re.search(json_obj_pattern, text, re.DOTALL | re.X)
        
        if match_obj:
            return match_obj.group(0)
            
        # Look for arrays
        json_arr_pattern = r"(\[(?:[^\[\]]|(?R))*\])"
        match_arr = re.search(json_arr_pattern, text, re.DOTALL | re.X)
        
        if match_arr:
            return match_arr.group(0)
    except re.error:
        # Fallback to simpler pattern if the recursive pattern isn't supported
        json_pattern = r"({[^{}]*(?:{[^{}]*}[^{}]*)*}|\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\])"
        match = re.search(json_pattern, text, re.DOTALL)
        
        if match:
            return match.group(0)
    
    # If we can't find JSON, return None
    logger.warning("No JSON found in text response")  # pragma: no cover
    return None


def parse_json_safely(json_str: str) -> Dict[str, Any]:
    """Parse JSON string safely, handling common errors.
    
    Args:
        json_str: The JSON string to parse.
        
    Returns:
        The parsed JSON as a dictionary.
        
    Raises:
        GeminiParsingError: If the JSON cannot be parsed.
    """
    if not json_str:  # pragma: no cover
        raise GeminiParsingError("Empty JSON string")
    
    try:
        # First try standard parsing
        return json.loads(json_str)
    except json.JSONDecodeError as e:  # pragma: no cover
        logger.warning(f"Standard JSON parsing failed: {str(e)}")
        
        # Try to fix common JSON issues
        fixed_json = fix_common_json_errors(json_str)
        try:
            return json.loads(fixed_json)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed after fixing: {str(e)}")
            raise GeminiParsingError(f"Failed to parse JSON: {str(e)}", json_str)


def fix_common_json_errors(json_str: str) -> str:  # pragma: no cover
    """Fix common JSON formatting errors in LLM outputs.
    
    Args:
        json_str: The JSON string to fix.
        
    Returns:
        The fixed JSON string.
    """
    # Replace single quotes with double quotes, but only for keys and string values
    fixed = re.sub(r"'([^']*)':", r'"\1":', json_str)
    fixed = re.sub(r":\s*'([^']*)'", r': "\1"', fixed)
    
    # Fix trailing commas in objects and arrays
    fixed = re.sub(r",\s*}", "}", fixed)
    fixed = re.sub(r",\s*\]", "]", fixed)
    
    # Fix missing commas between key-value pairs
    fixed = re.sub(r"}\s*{", "}, {", fixed)
    fixed = re.sub(r'"\s*{', '", {', fixed)
    fixed = re.sub(r'"\s*"', '", "', fixed)
    
    # Fix repeated colons
    fixed = re.sub(r":+", ":", fixed)
    
    # Fix extra/missing brackets
    bracket_stack = []
    for char in fixed:
        if char in "{[":
            bracket_stack.append(char)
        elif char in "}]":
            if bracket_stack and ((char == "}" and bracket_stack[-1] == "{") or 
                                 (char == "]" and bracket_stack[-1] == "[")):
                bracket_stack.pop()
    
    # Add missing closing brackets
    for bracket in reversed(bracket_stack):
        if bracket == "{":
            fixed += "}"
        elif bracket == "[":
            fixed += "]"
    
    # Fix escaped quotes
    fixed = fixed.replace('\\"', '"')
    fixed = fixed.replace('\\"', '"')
    
    logger.debug(f"Fixed JSON: {fixed[:100]}...")
    return fixed


def extract_fields(data: Dict[str, Any], field_path: str, default: Any = None) -> Any:  # pragma: no cover
    """Extract fields from a nested dictionary using a dot-separated path.
    
    Args:
        data: The dictionary to extract from.
        field_path: The dot-separated path to the field.
        default: The default value to return if the field is not found.
        
    Returns:
        The value of the field, or the default value if not found.
    """
    if not data:
        return default
    
    parts = field_path.split('.')
    current = data
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default
    
    return current 