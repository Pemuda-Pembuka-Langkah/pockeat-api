"""
Tests for the exercise analysis models.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from api.models.exercise_analysis import (
    ExerciseAnalysisResult,
    ExerciseAnalysisRequest,
    ExerciseCorrectionRequest
)

class TestExerciseAnalysisResult:
    """Tests for the ExerciseAnalysisResult model."""
    
    def test_exercise_analysis_result_creation(self):
        """Test creating an exercise analysis result with full values."""
        result = ExerciseAnalysisResult(
            exercise_type="Running",
            calories_burned=300,
            duration="30 minutes",
            intensity="high"
        )
        
        assert result.exercise_type == "Running"
        assert result.calories_burned == 300
        assert result.duration == "30 minutes"
        assert result.intensity == "high"
        assert result.error is None
        assert isinstance(result.timestamp, datetime)
        assert result.id is not None  # Auto-generated
    
    def test_exercise_analysis_result_defaults(self):
        """Test default values for exercise analysis result."""
        result = ExerciseAnalysisResult(
            exercise_type="Walking",
            calories_burned=150,
            duration="20 minutes",
            intensity="medium"
        )
        
        assert result.error is None
    
    def test_exercise_analysis_result_with_error(self):
        """Test exercise analysis result with error."""
        result = ExerciseAnalysisResult(
            exercise_type="unknown",
            calories_burned=0,
            duration="unknown",
            intensity="unknown",
            error="Failed to analyze exercise"
        )
        
        assert result.exercise_type == "unknown"
        assert result.calories_burned == 0
        assert result.duration == "unknown"
        assert result.intensity == "unknown"
        assert result.error == "Failed to analyze exercise"
    
    def test_exercise_analysis_result_validation(self):
        """Test validation of required fields."""
        # All fields are required
        with pytest.raises(Exception):
            ExerciseAnalysisResult(
                calories_burned=300,
                duration="30 minutes",
                intensity="high"
            )
        
        with pytest.raises(Exception):
            ExerciseAnalysisResult(
                exercise_type="Running",
                duration="30 minutes",
                intensity="high"
            )
        
        with pytest.raises(Exception):
            ExerciseAnalysisResult(
                exercise_type="Running",
                calories_burned=300,
                intensity="high"
            )
        
        with pytest.raises(Exception):
            ExerciseAnalysisResult(
                exercise_type="Running",
                calories_burned=300,
                duration="30 minutes"
            )

class TestExerciseAnalysisRequest:
    """Tests for the ExerciseAnalysisRequest model."""
    
    def test_exercise_analysis_request_creation(self):
        """Test creating an exercise analysis request with all fields."""
        request = ExerciseAnalysisRequest(
            description="Running for 30 minutes at high intensity",
            user_weight_kg=70.5
        )
        
        assert request.description == "Running for 30 minutes at high intensity"
        assert request.user_weight_kg == 70.5
    
    def test_exercise_analysis_request_defaults(self):
        """Test default values for exercise analysis request."""
        request = ExerciseAnalysisRequest(
            description="Walking for 20 minutes"
        )
        
        assert request.description == "Walking for 20 minutes"
        assert request.user_weight_kg is None  # Default
    
    def test_exercise_analysis_request_validation(self):
        """Test validation of required fields."""
        # Description is required
        with pytest.raises(Exception):
            ExerciseAnalysisRequest(user_weight_kg=70.5)

class TestExerciseCorrectionRequest:
    """Tests for the ExerciseCorrectionRequest model."""
    
    def test_exercise_correction_request_creation(self):
        """Test creating an exercise correction request."""
        previous_result = ExerciseAnalysisResult(
            exercise_type="Running",
            calories_burned=300,
            duration="30 minutes",
            intensity="high"
        )
        
        request = ExerciseCorrectionRequest(
            previous_result=previous_result,
            user_comment="Actually it was medium intensity"
        )
        
        assert request.previous_result == previous_result
        assert request.user_comment == "Actually it was medium intensity"
    
    def test_exercise_correction_request_validation(self):
        """Test validation of required fields."""
        # Both fields are required
        previous_result = ExerciseAnalysisResult(
            exercise_type="Running",
            calories_burned=300,
            duration="30 minutes",
            intensity="high"
        )
        
        with pytest.raises(Exception):
            ExerciseCorrectionRequest(previous_result=previous_result)
        
        with pytest.raises(Exception):
            ExerciseCorrectionRequest(user_comment="This needs correction") 