"""
Tests for the JSON utilities.
"""
import pytest

# Import the utilities that don't exist yet (RED phase)
from app.utils.json_utils import parse_json_response, validate_json_schema


class TestJsonUtils:
    """Test suite for the JSON utilities."""
    
    def test_parse_json_response_valid(self):
        """Test parsing a valid JSON response."""
        # RED: This will fail because the utility doesn't exist yet
        json_string = '{"name": "John", "age": 30}'
        result = parse_json_response(json_string)
        
        assert isinstance(result, dict)
        assert result["name"] == "John"
        assert result["age"] == 30
    
    def test_parse_json_response_invalid(self):
        """Test parsing an invalid JSON response."""
        # RED: This will fail because the utility doesn't exist yet
        json_string = '{name: "John", age: 30}'  # Invalid JSON (missing quotes)
        
        with pytest.raises(ValueError):
            parse_json_response(json_string)
    
    def test_parse_json_response_with_cleanup(self):
        """Test parsing a JSON response that needs cleanup."""
        # RED: This will fail because the utility doesn't exist yet
        # JSON wrapped in markdown or other text
        json_string = '''
        Here's your JSON analysis:
        ```json
        {"name": "John", "age": 30}
        ```
        Hope this helps!
        '''
        
        result = parse_json_response(json_string)
        assert isinstance(result, dict)
        assert result["name"] == "John"
        assert result["age"] == 30
    
    def test_validate_json_schema(self):
        """Test JSON schema validation."""
        # RED: This will fail because the utility doesn't exist yet
        schema = {
            "type": "object",
            "required": ["food", "calories"],
            "properties": {
                "food": {"type": "string"},
                "calories": {"type": "number"}
            }
        }
        
        # Valid data
        valid_data = {"food": "Apple", "calories": 52}
        assert validate_json_schema(valid_data, schema) is True
        
        # Invalid data (missing required field)
        invalid_data = {"food": "Apple"}
        assert validate_json_schema(invalid_data, schema) is False
        
        # Invalid data (wrong type)
        invalid_data2 = {"food": "Apple", "calories": "fifty-two"}
        assert validate_json_schema(invalid_data2, schema) is False 