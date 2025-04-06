"""
Integration tests for API routes.
"""

import os
import sys
import pytest
import json
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path so we can import from main.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from fastapi.testclient import TestClient
from main import app
from api.models.food_analysis import FoodAnalysisResult, NutritionInfo, Ingredient
from api.models.exercise_analysis import ExerciseAnalysisResult
from api.services.gemini_service import GeminiService

# Mock the GeminiService before it's imported by routes
mock_gemini_service = MagicMock(spec=GeminiService)

class TestAPIRoutes:
    """Test API routes."""
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self):
        """Setup for the test class to mock GeminiService."""
        # Create a patcher for the GeminiService initialization
        with patch("api.routes.GeminiService", return_value=mock_gemini_service) as mock_init:
            # This makes sure the GeminiService is mocked at initialization
            mock_init.return_value = mock_gemini_service
            # Also patch the gemini_service in the routes module directly
            with patch("api.routes.gemini_service", mock_gemini_service):
                yield
    
    @pytest.fixture
    def client(self):
        """Create a test client with authentication disabled."""
        # Store original environment
        original_env = os.environ.copy()
        
        # Instead of changing environment variables, we'll patch the authentication function
        with patch("api.dependencies.auth.optional_verify_token") as mock_verify:
            # Configure the mock to return a valid user
            mock_verify.return_value = {
                "uid": "test-user-id",
                "email": "test@example.com",
                "name": "Test User"
            }
            
            # Create test client
            with TestClient(app) as test_client:
                yield test_client
                
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)

    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        print(f"Root endpoint response: {response.json()}")
        assert response.status_code == 200
        # Check only status key as message might vary
        assert response.json()["status"] == "healthy"

    def test_health_check(self, client):
        """Test the health check endpoint."""
        # Mock the check_health method for this test
        mock_gemini_service.check_health.return_value = True
        
        response = client.get("/api/health")
        # Print response for debugging
        print(f"Health check response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_health_check_service_unavailable(self, client):
        """Test the health check when Gemini service is unavailable."""
        # Mock the check_health method for this test
        mock_gemini_service.check_health.return_value = False
        
        response = client.get("/api/health")
        # Print response for debugging
        print(f"Health check response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["status"] == "degraded"

    def test_debug_environment(self, client):
        """Test the debug environment endpoint."""
        response = client.get("/debug-env")
        assert response.status_code == 200
        assert "has_key" in response.json()

    def test_analyze_food_by_text(self, client):
        """Test analyzing food by text."""
        mock_result = FoodAnalysisResult(
            food_name="Test Food",
            ingredients=[Ingredient(name="Ingredient 1", servings=100)],
            nutrition_info=NutritionInfo(calories=200)
        )
        
        # Mock the analyze_food_by_text method for this test
        mock_gemini_service.analyze_food_by_text.return_value = mock_result
        
        response = client.post(
            "/api/food/analyze/text",
            json={"description": "test food"}
        )
        assert response.status_code == 200
        assert response.json()["food_name"] == "Test Food"
        assert len(response.json()["ingredients"]) == 1
        assert response.json()["nutrition_info"]["calories"] == 200

    def test_analyze_food_by_text_service_unavailable(self, client):
        """Test analyzing food by text when service is unavailable."""
        # Mock the analyze_food_by_text method to raise an exception
        mock_gemini_service.analyze_food_by_text.side_effect = Exception("Service unavailable")
        
        response = client.post(
            "/api/food/analyze/text",
            json={"description": "test food"}
        )
        # Print response for debugging
        print(f"Error response: {response.json()}")
        assert response.status_code == 500
        assert "detail" in response.json()

    def test_analyze_exercise(self, client):
        """Test analyzing exercise."""
        mock_result = ExerciseAnalysisResult(
            exercise_type="Running",
            duration="30 minutes",
            intensity="High",
            calories_burned=350
        )
        
        # Mock the analyze_exercise method for this test
        mock_gemini_service.analyze_exercise.return_value = mock_result
        
        response = client.post(
            "/api/exercise/analyze",
            json={"description": "running for 30 minutes", "user_weight_kg": 70.5}
        )
        assert response.status_code == 200
        assert response.json()["exercise_type"] == "Running"

    def test_analyze_exercise_service_unavailable(self, client):
        """Test analyzing exercise when service is unavailable."""
        # Mock the analyze_exercise method to raise an exception
        mock_gemini_service.analyze_exercise.side_effect = Exception("Service unavailable")
        
        response = client.post(
            "/api/exercise/analyze",
            json={"description": "running for 30 minutes"}
        )
        # Print response for debugging
        print(f"Error response: {response.json()}")
        assert response.status_code == 500
        assert "detail" in response.json()

    def test_correct_food_analysis(self, client):
        """Test correcting food analysis."""
        previous_result = FoodAnalysisResult(
            food_name="Test Food",
            ingredients=[Ingredient(name="Ingredient 1", servings=100)],
            nutrition_info=NutritionInfo(calories=200)
        )
        
        corrected_result = FoodAnalysisResult(
            food_name="Corrected Food",
            ingredients=[Ingredient(name="Ingredient 1", servings=150)],
            nutrition_info=NutritionInfo(calories=250)
        )
        
        # Mock the correct_food_analysis method for this test
        mock_gemini_service.correct_food_analysis.return_value = corrected_result
        
        # Convert the previous result to dict and remove the timestamp field
        previous_result_dict = previous_result.dict()
        if "timestamp" in previous_result_dict:
            previous_result_dict.pop("timestamp")
            
        response = client.post(
            "/api/food/correct/text",
            json={
                "previous_result": previous_result_dict,
                "user_comment": "correction comment"
            }
        )
        assert response.status_code == 200
        assert response.json()["food_name"] == "Corrected Food"
        assert response.json()["nutrition_info"]["calories"] == 250

    def test_correct_exercise_analysis(self, client):
        """Test correcting exercise analysis."""
        previous_result = ExerciseAnalysisResult(
            exercise_type="Jogging",
            duration="30 minutes",
            intensity="Medium",
            calories_burned=250
        )
        
        corrected_result = ExerciseAnalysisResult(
            exercise_type="Running",
            duration="30 minutes",
            intensity="High",
            calories_burned=350
        )
        
        # Mock the correct_exercise_analysis method for this test
        mock_gemini_service.correct_exercise_analysis.return_value = corrected_result
        
        # Convert the previous result to dict and remove the timestamp field
        previous_result_dict = previous_result.dict()
        if "timestamp" in previous_result_dict:
            previous_result_dict.pop("timestamp")
            
        response = client.post(
            "/api/exercise/correct",
            json={
                "previous_result": previous_result_dict,
                "user_comment": "correction comment"
            }
        )
        assert response.status_code == 200
        assert response.json()["exercise_type"] == "Running"

    @pytest.mark.asyncio
    async def test_analyze_food_by_image(self, client):
        """Test analyzing food by image."""
        mock_result = FoodAnalysisResult(
            food_name="Pizza",
            ingredients=[Ingredient(name="Cheese", servings=50)],
            nutrition_info=NutritionInfo(calories=450)
        )
        
        # Mock the _read_image_bytes method to avoid image validation
        mock_gemini_service.analyze_food_by_image.return_value = mock_result
        
        # Create a simple mock image file
        mock_image_content = b"This is a mock food image for testing"
        
        # Use multipart/form-data to upload file and provide description
        response = client.post(
            "/api/food/analyze/image",
            files={"image": ("test_image.jpg", mock_image_content, "image/jpeg")}
        )
        
        # Print response for debugging
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content}")
        
        assert response.status_code == 200
        assert response.json()["food_name"] == "Pizza"
        assert response.json()["nutrition_info"]["calories"] == 450

    @pytest.mark.asyncio
    async def test_analyze_nutrition_label(self, client):
        """Test analyzing nutrition label."""
        mock_result = FoodAnalysisResult(
            food_name="Nutrition Facts",
            ingredients=[],
            nutrition_info=NutritionInfo(calories=200, protein=15)
        )
        
        # Mock the analyze_nutrition_label method to return our mock result
        mock_gemini_service.analyze_nutrition_label.return_value = mock_result
        
        # Create a simple mock image file
        mock_image_content = b"This is a mock nutrition label for testing"
        
        # Use multipart/form-data to upload file
        response = client.post(
            "/api/food/analyze/nutrition-label",
            files={"image": ("nutrition_label.jpg", mock_image_content, "image/jpeg")},
            data={"servings": "2.0"}
        )
        
        # Print response for debugging
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content}")
        
        assert response.status_code == 200
        assert response.json()["food_name"] == "Nutrition Facts"
        assert response.json()["nutrition_info"]["calories"] == 200
        assert response.json()["nutrition_info"]["protein"] == 15 