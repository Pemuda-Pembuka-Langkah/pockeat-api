"""
Exercise analysis models using Pydantic for FastAPI.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import uuid4
from pydantic import BaseModel, Field, validator


class ExerciseAnalysisResult(BaseModel):
    """Exercise analysis result model."""
    
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier")
    exercise_type: str = Field(description="Type of exercise (e.g., cardio, strength)")
    duration: str = Field(description="Duration of the exercise (as a string)")
    intensity: str = Field(description="Exercise intensity (low, medium, high)")
    calories_burned: float = Field(description="Estimated calories burned")
    met_value: float = Field(default=0.0, description="MET (Metabolic Equivalent of Task) value")
    summary: Optional[str] = Field(default=None, description="Summary of the exercise analysis")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of analysis")
    original_input: str = Field(description="Original exercise description input")
    missing_info: Optional[List[str]] = Field(default=None, description="List of missing information fields")
    error: Optional[str] = Field(default=None, description="Error message if analysis failed")
    
    @property
    def is_complete(self) -> bool:
        """Check if all required information is present."""
        return self.missing_info is None or len(self.missing_info) == 0
    
    def to_map(self) -> Dict[str, Any]:
        """Convert to a map similar to the Dart toMap() method."""
        return {
            "exerciseType": self.exercise_type,
            "duration": self.duration,
            "intensity": self.intensity,
            "estimatedCalories": self.calories_burned,
            "metValue": self.met_value,
            "summary": self.summary,
            "timestamp": int(self.timestamp.timestamp() * 1000),
            "originalInput": self.original_input,
            "missingInfo": self.missing_info,
            "isComplete": self.is_complete,
        }
    
    @classmethod
    def from_map(cls, map_data: Dict[str, Any], id: Optional[str] = None) -> "ExerciseAnalysisResult":
        """Create an instance from a map similar to the Dart fromDbMap method."""
        if id is None:
            id = str(uuid4())
        
        timestamp = datetime.now()
        if "timestamp" in map_data and map_data["timestamp"] is not None:
            # Convert milliseconds to datetime
            timestamp = datetime.fromtimestamp(map_data["timestamp"] / 1000)
        
        return cls(
            id=id,
            exercise_type=map_data.get("exerciseType", "Unknown"),
            duration=map_data.get("duration", "Not specified"),
            intensity=map_data.get("intensity", "Not specified"),
            calories_burned=map_data.get("estimatedCalories", 0),
            met_value=float(map_data.get("metValue", 0.0)),
            summary=map_data.get("summary"),
            timestamp=timestamp,
            original_input=map_data.get("originalInput", ""),
            missing_info=map_data.get("missingInfo"),
        )
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "exercise_type": "cardio",
                "duration": "30 minutes",
                "intensity": "medium", 
                "calories_burned": 300,
                "met_value": 7.0,
                "summary": "You performed cardio for 30 minutes at medium intensity, burning approximately 300 calories.",
                "timestamp": "2023-03-25T12:00:00Z",
                "original_input": "30 minute run at 8 km/h pace",
                "missing_info": []
            }
        }


class ExerciseAnalysisRequest(BaseModel):
    """Exercise analysis request model."""
    
    description: str = Field(description="Description of the exercise to analyze")
    user_weight_kg: Optional[float] = Field(default=None, description="User's weight in kilograms for calorie calculation")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "description": "30 minute run at 8 km/h pace",
                "user_weight_kg": 70
            }
        }


class ExerciseCorrectionRequest(BaseModel):
    """Exercise correction request model."""
    
    previous_result: ExerciseAnalysisResult = Field(description="Previous analysis result to correct")
    user_comment: str = Field(description="User's feedback for correction")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "previous_result": {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "exercise_type": "cardio",
                    "duration": "30 minutes",
                    "intensity": "medium",
                    "calories_burned": 300,
                    "met_value": 7.0,
                    "summary": "You performed cardio for 30 minutes at medium intensity, burning approximately 300 calories.",
                    "timestamp": "2023-03-25T12:00:00Z",
                    "original_input": "30 minute run at 8 km/h pace",
                    "missing_info": []
                },
                "user_comment": "I actually ran for 45 minutes, not 30"
            }
        } 