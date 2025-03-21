"""
Tests for the Exercise Analysis Service.
"""
import pytest
from unittest.mock import patch, MagicMock

# Import the service that doesn't exist yet (RED phase)
from app.services.exercise.exercise_analysis_service import ExerciseAnalysisService


class TestExerciseAnalysisService:
    """Test suite for the ExerciseAnalysisService class."""

    def test_initialization(self):
        """Test that the service initializes with Gemini client."""
        # Setup mock
        mock_gemini_client = MagicMock()
        
        # RED: This will fail because the service doesn't exist yet
        service = ExerciseAnalysisService(gemini_client=mock_gemini_client)
        assert service.gemini_client == mock_gemini_client
    
    @patch('app.services.exercise.exercise_analysis_service.ExerciseAnalysisService._format_prompt')
    def test_analyze_exercise(self, mock_format_prompt):
        """Test analyzing exercise description."""
        # Setup mocks
        mock_gemini_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"exercise": "Running", "calories_burned": 300, "duration_minutes": 30, "intensity": "moderate"}'
        mock_gemini_client.generate_content.return_value = mock_response
        mock_format_prompt.return_value = "Analyze this exercise"
        
        # RED: This will fail because the service doesn't exist yet
        service = ExerciseAnalysisService(gemini_client=mock_gemini_client)
        result = service.analyze_exercise("I ran for 30 minutes at a moderate pace")
        
        # Assertions
        mock_gemini_client.generate_content.assert_called_once()
        assert isinstance(result, dict)
        assert result["exercise"] == "Running"
        assert result["calories_burned"] == 300
        assert result["duration_minutes"] == 30
    
    def test_format_prompt(self):
        """Test that the prompt is correctly formatted."""
        # Setup mock
        mock_gemini_client = MagicMock()
        
        # RED: This will fail because the service doesn't exist yet
        service = ExerciseAnalysisService(gemini_client=mock_gemini_client)
        prompt = service._format_prompt("I ran for 30 minutes")
        
        # Assertions
        assert "JSON" in prompt
        assert "exercise" in prompt
        assert "calories_burned" in prompt 