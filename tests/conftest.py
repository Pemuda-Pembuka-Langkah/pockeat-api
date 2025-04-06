"""
Common test fixtures for all tests.
"""

import os
import sys
import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path so we can import from main.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

# Setup Firebase-related mocks
@pytest.fixture
def mock_firebase_admin():
    """Mock firebase_admin module for testing."""
    with patch("firebase_admin.initialize_app"), \
         patch("firebase_admin.credentials.Certificate"), \
         patch("firebase_admin.auth.verify_id_token") as mock_verify:
        
        # Configure mock to return a valid user by default
        mock_verify.return_value = {
            "uid": "test-user-id",
            "email": "test@example.com",
            "name": "Test User"
        }
        yield mock_verify

@pytest.fixture
def test_client():
    """Create a test client for FastAPI app."""
    # Disable auth for tests
    os.environ["GLOBAL_AUTH_ENABLED"] = "false"
    with TestClient(app) as client:
        yield client
    # Restore default
    os.environ["GLOBAL_AUTH_ENABLED"] = "true"

@pytest.fixture
def test_client_with_mock_firebase(mock_firebase_admin):
    """Create a test client with mocked Firebase."""
    # Disable auth for tests
    os.environ["GLOBAL_AUTH_ENABLED"] = "false"
    with TestClient(app) as client:
        yield client
    # Restore default
    os.environ["GLOBAL_AUTH_ENABLED"] = "true"

@pytest.fixture
def auth_headers():
    """Headers with a valid auth token."""
    return {"Authorization": "Bearer valid-test-token"}

@pytest.fixture
def invalid_auth_headers():
    """Headers with an invalid auth token."""
    return {"Authorization": "Bearer invalid-token"}

@pytest.fixture
def mock_gemini_text_response():  # pragma: no cover
    """Mock successful response from Gemini text model."""
    mock_response = MagicMock()
    mock_response.content.candidates.text = json.dumps({
        "food_name": "Test Food",
        "ingredients": [{"name": "Ingredient 1", "servings": 100}],
        "nutrition_info": {
            "calories": 200,
            "protein": 10,
            "carbs": 20,
            "fat": 5,
            "sodium": 100,
            "fiber": 2,
            "sugar": 5
        }
    })
    return mock_response

@pytest.fixture
def mock_gemini_service():  # pragma: no cover
    """Mock the entire GeminiService for testing."""
    with patch("api.services.gemini_service.GeminiService") as mock_service:
        instance = mock_service.return_value
        
        # Configure instance methods
        instance.check_health.return_value = True
        instance.analyze_food_by_text.return_value = {
            "food_name": "Test Food",
            "ingredients": [{"name": "Ingredient 1", "servings": 100}],
            "nutrition_info": {
                "calories": 200,
                "protein": 10,
                "carbs": 20,
                "fat": 5,
                "sodium": 100,
                "fiber": 2,
                "sugar": 5
            }
        }
        instance.analyze_exercise.return_value = {
            "exercise_type": "Running",
            "calories_burned": 500,
            "duration": "30 minutes",
            "intensity": "high"
        }
        
        yield instance

# Environment fixture to set necessary environment variables
@pytest.fixture
def env_vars():
    """Set environment variables for testing."""
    original_env = os.environ.copy()
    os.environ["GOOGLE_API_KEY"] = "fake-api-key"
    os.environ["GLOBAL_AUTH_ENABLED"] = "false"  # Disable auth for tests
    yield
    os.environ.clear()
    os.environ.update(original_env)

# Fixture to specifically disable auth for tests
@pytest.fixture(autouse=True)
def disable_auth_for_tests():  # pragma: no cover
    """Disable authentication globally for all tests."""
    original_auth_setting = os.environ.get("GLOBAL_AUTH_ENABLED", "true")
    os.environ["GLOBAL_AUTH_ENABLED"] = "false"
    yield
    os.environ["GLOBAL_AUTH_ENABLED"] = original_auth_setting

@pytest.fixture(scope="session", autouse=True)
def disable_auth():  # pragma: no cover
    """
    Disable authentication for tests by patching the verify_token function
    to always return a successful result.
    """
    # Create a mock function that always returns success
    def mock_verify_token(token=None):
        return {"uid": "test-user-id", "email": "test@example.com"}
    
    # Patch the verify_token function in the auth dependency
    with patch("api.dependencies.auth.verify_token", side_effect=mock_verify_token):
        yield 