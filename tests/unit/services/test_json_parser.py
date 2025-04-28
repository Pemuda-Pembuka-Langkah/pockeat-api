"""
Tests for JSON parser utilities.
"""

import json
import pytest
from api.services.gemini.utils.json_parser import (
    extract_json_from_text,
    parse_json_safely,
    fix_common_json_errors,
    extract_fields,
)
from api.services.gemini.exceptions import GeminiParsingError


class TestJsonParser:
    """Test suite for JSON parser utilities."""

    def test_extract_json_from_text_markdown(self):
        """Test extracting JSON from markdown code blocks."""
        text = """
        Here's some text
        ```json
        {"key": "value"}
        ```
        More text
        """
        result = extract_json_from_text(text)
        assert result == '{"key": "value"}'

    def test_extract_json_from_text_no_markdown(self):
        """Test extracting JSON without markdown code blocks."""
        text = 'Some text {"key": "value"} more text'
        result = extract_json_from_text(text)
        assert result == '{"key": "value"}'

    def test_extract_json_from_text_array(self):
        """Test extracting JSON array."""
        text = 'Text [1, 2, 3] more text'
        result = extract_json_from_text(text)
        assert result == '[1, 2, 3]'

    def test_extract_json_from_text_nested(self):
        """Test extracting nested JSON."""
        text = 'Text {"outer": {"inner": "value"}} more text'
        result = extract_json_from_text(text)
        assert result == '{"outer": {"inner": "value"}}'

    def test_extract_json_from_text_no_json(self):
        """Test extracting when no JSON is present."""
        text = "Just plain text"
        result = extract_json_from_text(text)
        assert result is None

    def test_parse_json_safely_valid(self):
        """Test parsing valid JSON."""
        json_str = '{"key": "value"}'
        result = parse_json_safely(json_str)
        assert result == {"key": "value"}

    def test_parse_json_safely_invalid(self):
        """Test parsing invalid JSON."""
        json_str = '{"key": "value"'
        with pytest.raises(GeminiParsingError):
            parse_json_safely(json_str)

    def test_parse_json_safely_empty(self):
        """Test parsing empty JSON string."""
        with pytest.raises(GeminiParsingError):
            parse_json_safely("")

    def test_fix_common_json_errors_single_quotes(self):
        """Test fixing single quotes in JSON."""
        json_str = "{'key': 'value'}"
        fixed = fix_common_json_errors(json_str)
        assert fixed == '{"key": "value"}'

    def test_fix_common_json_errors_trailing_comma(self):
        """Test fixing trailing commas in JSON."""
        json_str = '{"key": "value",}'
        fixed = fix_common_json_errors(json_str)
        assert fixed == '{"key": "value"}'

    def test_fix_common_json_errors_missing_comma(self):
        """Test fixing missing commas in JSON."""
        json_str = '{"key1": "value1" "key2": "value2"}'
        fixed = fix_common_json_errors(json_str)
        assert fixed == '{"key1": "value1", "key2": "value2"}'

    def test_fix_common_json_errors_extra_colons(self):
        """Test fixing extra colons in JSON."""
        json_str = '{"key":: "value"}'
        fixed = fix_common_json_errors(json_str)
        assert fixed == '{"key": "value"}'

    def test_fix_common_json_errors_missing_brackets(self):
        """Test fixing missing brackets in JSON."""
        json_str = '{"key": "value"'
        fixed = fix_common_json_errors(json_str)
        assert fixed == '{"key": "value"}'

    def test_fix_common_json_errors_escaped_quotes(self):
        """Test fixing escaped quotes in JSON."""
        json_str = '{"key": "\\"value\\""}'
        fixed = fix_common_json_errors(json_str)
        assert fixed == '{"key": "value"}'

    def test_extract_fields_simple(self):
        """Test extracting simple field path."""
        data = {"key": "value"}
        result = extract_fields(data, "key")
        assert result == "value"

    def test_extract_fields_nested(self):
        """Test extracting nested field path."""
        data = {"outer": {"inner": "value"}}
        result = extract_fields(data, "outer.inner")
        assert result == "value"

    def test_extract_fields_missing(self):
        """Test extracting missing field path."""
        data = {"key": "value"}
        result = extract_fields(data, "missing", default="default")
        assert result == "default"

    def test_extract_fields_empty_data(self):
        """Test extracting from empty data."""
        result = extract_fields({}, "key", default="default")
        assert result == "default"

    def test_extract_fields_invalid_path(self):
        """Test extracting with invalid path."""
        data = {"key": "value"}
        result = extract_fields(data, "key.missing", default="default")
        assert result == "default" 