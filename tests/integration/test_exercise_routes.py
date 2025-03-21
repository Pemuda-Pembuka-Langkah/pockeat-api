"""
Integration tests for the exercise analysis routes.
"""
import pytest
import json
from unittest.mock import patch


class TestExerciseRoutes:
    """Test suite for the exercise analysis routes."""
    
    @patch('app.services.exercise.exercise_analysis_service.ExerciseAnalysisService.analyze_exercise')
    def test_analyze_exercise_endpoint(self, mock_analyze_exercise, client):
        """Test the exercise analysis endpoint."""
        # Setup mock
        mock_analyze_exercise.return_value = {
            "exercise": "Running", 
            "calories_burned": 300, 
            "duration_minutes": 30, 
            "intensity": "moderate"
        }
        
        # Make request
        response = client.post(
            '/api/v1/exercise/analyze',
            json={
                'description': 'I ran for 30 minutes at a moderate pace'
            }
        )
        
        # Assertions
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['exercise'] == 'Running'
        assert data['calories_burned'] == 300
        assert data['duration_minutes'] == 30
        
    @patch('app.services.exercise.exercise_correction_service.ExerciseCorrectionService.correct_exercise_entry')
    def test_correct_exercise_entry_endpoint(self, mock_correct_exercise, client):
        """Test the exercise correction endpoint."""
        # Setup mock
        mock_correct_exercise.return_value = {
            "exercise": "Speed Walking", 
            "calories_burned": 200,
            "duration_minutes": 45,
            "intensity": "light"
        }
        
        # Make request
        response = client.post(
            '/api/v1/exercise/correct',
            json={
                'exercise_entry': 'I walked quickly for 45 mins',
                'user_correction': 'It was actually speed walking, not running'
            }
        )
        
        # Assertions
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['exercise'] == 'Speed Walking'
        assert data['calories_burned'] == 200
        assert data['intensity'] == 'light' 