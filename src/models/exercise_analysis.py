"""
Models for exercise analysis.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4


@dataclass
class ExerciseAnalysisResult:
    """Exercise analysis result model."""
    
    # Constants for intensity levels for consistency
    INTENSITY_LOW = "low"
    INTENSITY_MODERATE = "moderate"
    INTENSITY_HIGH = "high"
    
    id: str
    exercise_type: str
    calories_burned: float
    duration_minutes: float
    intensity_level: str
    met_value: float
    description: str
    timestamp: datetime = None
    
    def __post_init__(self):
        """Post initialization."""
        # Generate ID if not provided
        if not hasattr(self, 'id') or not self.id:
            self.id = str(uuid4())
        
        # Set timestamp if not provided
        if not self.timestamp:
            self.timestamp = datetime.now()
        
        # Normalize intensity level
        self.intensity_level = self._normalize_intensity_level(self.intensity_level)
    
    @staticmethod
    def _normalize_intensity_level(intensity: str) -> str:
        """Normalize intensity level to one of the predefined levels.
        
        Args:
            intensity: The intensity level.
            
        Returns:
            The normalized intensity level.
        """
        intensity = intensity.lower()
        
        if "low" in intensity or "light" in intensity or "mild" in intensity:
            return ExerciseAnalysisResult.INTENSITY_LOW
        elif "high" in intensity or "vigorous" in intensity or "intense" in intensity:
            return ExerciseAnalysisResult.INTENSITY_HIGH
        else:
            return ExerciseAnalysisResult.INTENSITY_MODERATE
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], id: Optional[str] = None) -> 'ExerciseAnalysisResult':
        """Create an ExerciseAnalysisResult from a dictionary.
        
        Args:
            data: The dictionary.
            id: The ID to use.
            
        Returns:
            The ExerciseAnalysisResult.
        """
        # Parse timestamp
        timestamp = datetime.now()
        if 'timestamp' in data:
            try:
                if isinstance(data['timestamp'], int):
                    timestamp = datetime.fromtimestamp(data['timestamp'] / 1000.0)
            except (ValueError, TypeError):
                pass
        
        # Handle potential different field names for calories
        calories = data.get('calories_burned', data.get('estimated_calories', 0.0))
        if isinstance(calories, str):
            try:
                calories = float(calories)
            except (ValueError, TypeError):
                calories = 0.0
        
        # Handle potential different field names for duration
        duration = data.get('duration_minutes', 0.0)
        if isinstance(duration, str):
            # Try to extract minutes from strings like "30 minutes"
            import re
            duration_match = re.search(r'(\d+)', str(duration))
            duration = float(duration_match.group(1)) if duration_match else 0.0
        
        # Create and return the ExerciseAnalysisResult
        return cls(
            id=id or data.get('id', str(uuid4())),
            exercise_type=data.get('exercise_type', ''),
            calories_burned=float(calories),
            duration_minutes=float(duration),
            intensity_level=data.get('intensity_level', 'moderate'),
            met_value=float(data.get('met_value', 0.0)),
            description=data.get('description', data.get('original_input', '')),
            timestamp=timestamp
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the ExerciseAnalysisResult to a dictionary.
        
        Returns:
            The dictionary.
        """
        return {
            'id': self.id,
            'exercise_type': self.exercise_type,
            'calories_burned': self.calories_burned,
            'duration_minutes': self.duration_minutes,
            'intensity_level': self.intensity_level,
            'met_value': self.met_value,
            'description': self.description,
            'timestamp': int(self.timestamp.timestamp() * 1000)
        }
    
    def copy_with(self, **kwargs) -> 'ExerciseAnalysisResult':
        """Create a copy of the ExerciseAnalysisResult with updated fields.
        
        Args:
            **kwargs: The fields to update.
            
        Returns:
            The updated ExerciseAnalysisResult.
        """
        data = self.to_dict()
        data.update(kwargs)
        return self.from_dict(data, id=self.id) 