"""
Unit tests for food routes.
"""
import io
import json
from unittest.mock import patch, MagicMock
import pytest
from flask import Flask
from app.api.routes.food_routes import food_bp


@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['GEMINI_API_KEY'] = 'test-api-key'
    app.register_blueprint(food_bp)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def mock_food_analysis_service():
    """Create a mock for the food analysis service."""
    mock = MagicMock()
    mock.analyze_food_image.return_value = {
        "food": "Test Food",
        "calories": 200,
        "protein": 10,
        "fat": 5,
        "carbs": 30,
        "portion_size": "1 serving"
    }
    return mock


@pytest.fixture
def mock_food_correction_service():
    """Create a mock for the food correction service."""
    mock = MagicMock()
    mock.correct_food_entry.return_value = {
        "food": "Corrected Food",
        "calories": 250,
        "protein": 12,
        "fat": 6,
        "carbs": 35,
        "portion_size": "1 serving"
    }
    return mock


@patch('app.api.routes.food_routes.get_services')
def test_analyze_food_valid_request(mock_get_services, client, mock_food_analysis_service):
    """Test the /analyze endpoint with a valid request."""
    # Setup mock
    mock_get_services.return_value = (mock_food_analysis_service, None)
    
    # Create a test image file
    test_image = io.BytesIO(b'test image data')
    
    # Send the request
    response = client.post(
        '/food/analyze',
        data={'image': (test_image, 'test_image.jpg')},
        content_type='multipart/form-data'
    )
    
    # Check the response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['food'] == 'Test Food'
    assert data['calories'] == 200
    
    # Verify mock calls
    mock_food_analysis_service.analyze_food_image.assert_called_once()


@patch('app.api.routes.food_routes.get_services')
def test_analyze_food_missing_image(mock_get_services, client):
    """Test the /analyze endpoint with a missing image."""
    # Send the request without an image
    response = client.post('/food/analyze', data={})
    
    # Check the response
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'No image provided' in data['error']
    
    # Verify mock calls
    mock_get_services.assert_not_called()


@patch('app.api.routes.food_routes.get_services')
def test_text_analysis_valid_request(mock_get_services, client, mock_food_correction_service):
    """Test the /text endpoint with a valid request."""
    # Setup mock
    mock_get_services.return_value = (None, mock_food_correction_service)
    
    # Send the request
    response = client.post(
        '/food/text',
        json={'food_description': 'Chicken salad with tomatoes'},
        content_type='application/json'
    )
    
    # Check the response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['food'] == 'Corrected Food'
    
    # Verify mock calls
    mock_food_correction_service.correct_food_entry.assert_called_once_with(
        "", "Chicken salad with tomatoes"
    )


@patch('app.api.routes.food_routes.get_services')
def test_text_analysis_missing_description(mock_get_services, client):
    """Test the /text endpoint with a missing description."""
    # Send the request without a food_description
    response = client.post('/food/text', json={})
    
    # Check the response
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Missing food_description' in data['error']
    
    # Verify mock calls
    mock_get_services.assert_not_called()


@patch('app.api.routes.food_routes.get_services')
def test_nutrition_label_valid_request(mock_get_services, client, mock_food_analysis_service):
    """Test the /nutrition-label endpoint with a valid request."""
    # Setup mock
    mock_get_services.return_value = (mock_food_analysis_service, None)
    
    # Create a test image file
    test_image = io.BytesIO(b'test image data')
    
    # Send the request
    response = client.post(
        '/food/nutrition-label',
        data={
            'image': (test_image, 'nutrition_label.jpg'),
            'servings': '2.5'
        },
        content_type='multipart/form-data'
    )
    
    # Check the response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['food'] == 'Test Food'
    assert data['calories'] == 500  # 200 * 2.5
    assert data['protein'] == 25    # 10 * 2.5
    
    # Verify mock calls
    mock_food_analysis_service.analyze_food_image.assert_called_once()


@patch('app.api.routes.food_routes.get_services')
def test_nutrition_label_invalid_servings(mock_get_services, client):
    """Test the /nutrition-label endpoint with invalid servings."""
    # Create a test image file
    test_image = io.BytesIO(b'test image data')
    
    # Send the request with invalid servings
    response = client.post(
        '/food/nutrition-label',
        data={
            'image': (test_image, 'nutrition_label.jpg'),
            'servings': 'not-a-number'
        },
        content_type='multipart/form-data'
    )
    
    # Check the response
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Invalid servings value' in data['error']
    
    # Verify mock calls
    mock_get_services.assert_not_called()


@patch('app.api.routes.food_routes.get_services')
def test_correct_food_entry_valid_request(mock_get_services, client, mock_food_correction_service):
    """Test the /correct endpoint with a valid request."""
    # Setup mock
    mock_get_services.return_value = (None, mock_food_correction_service)
    
    # Send the request
    response = client.post(
        '/food/correct',
        json={
            'food_entry': 'Chicken salad',
            'user_correction': 'Add tomatoes'
        },
        content_type='application/json'
    )
    
    # Check the response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['food'] == 'Corrected Food'
    
    # Verify mock calls
    mock_food_correction_service.correct_food_entry.assert_called_once_with(
        'Chicken salad', 'Add tomatoes'
    )


@patch('app.api.routes.food_routes.get_services')
def test_correct_food_entry_missing_fields(mock_get_services, client):
    """Test the /correct endpoint with missing fields."""
    # Send the request with missing fields
    response = client.post(
        '/food/correct',
        json={'food_entry': 'Incomplete data'},
        content_type='application/json'
    )
    
    # Check the response
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Missing required fields' in data['error']
    
    # Verify mock calls
    mock_get_services.assert_not_called()


@patch('app.api.routes.food_routes.get_services')
def test_service_exception_handling(mock_get_services, client, mock_food_analysis_service):
    """Test exception handling in the routes."""
    # Setup mock to raise an exception
    mock_food_analysis_service.analyze_food_image.side_effect = Exception("Test error")
    mock_get_services.return_value = (mock_food_analysis_service, None)
    
    # Create a test image file
    test_image = io.BytesIO(b'test image data')
    
    # Send the request
    response = client.post(
        '/food/analyze',
        data={'image': (test_image, 'test_image.jpg')},
        content_type='multipart/form-data'
    )
    
    # Check the response
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Test error' in data['error'] 