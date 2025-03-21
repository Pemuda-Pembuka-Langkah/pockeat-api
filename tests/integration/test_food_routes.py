"""
Integration tests for the food analysis routes.
"""
import pytest
import json
from unittest.mock import patch
from io import BytesIO


class TestFoodRoutes:
    """Test suite for the food analysis routes."""
    
    @patch('app.services.food.food_analysis_service.FoodAnalysisService.analyze_food_image')
    def test_analyze_food_image_endpoint(self, mock_analyze_food, client):
        """Test the food image analysis endpoint."""
        # Setup mock
        mock_analyze_food.return_value = {
            "food": "Apple", 
            "calories": 52, 
            "protein": 0.3, 
            "fat": 0.2, 
            "carbs": 14
        }
        
        # Create a fake image
        fake_image = BytesIO(b"fake_image_bytes")
        
        # Make request with multipart form data
        response = client.post(
            '/api/v1/food/analyze',
            data={
                'image': (fake_image, 'food.jpg')
            },
            content_type='multipart/form-data'
        )
        
        # Assertions
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['food'] == 'Apple'
        assert data['calories'] == 52
        
    @patch('app.services.food.food_correction_service.FoodCorrectionService.correct_food_entry')
    def test_correct_food_entry_endpoint(self, mock_correct_food, client):
        """Test the food correction endpoint."""
        # Setup mock
        mock_correct_food.return_value = {
            "food": "Green Apple", 
            "calories": 50
        }
        
        # Make request
        response = client.post(
            '/api/v1/food/correct',
            json={
                'food_entry': 'I ate an aple',
                'user_correction': 'It was a green apple'
            }
        )
        
        # Assertions
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['food'] == 'Green Apple'
        assert data['calories'] == 50 