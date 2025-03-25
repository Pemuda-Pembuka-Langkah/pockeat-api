"""
Models for food analysis.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4


@dataclass
class Ingredient:
    """Ingredient model."""
    
    name: str
    servings: float
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Ingredient':
        """Create an Ingredient from a dictionary.
        
        Args:
            data: The dictionary.
            
        Returns:
            The Ingredient.
        """
        return cls(
            name=data.get('name', ''),
            servings=cls._parse_double(data.get('servings', 0.0))
        )
    
    def to_dict(self) -> dict:
        """Convert the Ingredient to a dictionary.
        
        Returns:
            The dictionary.
        """
        return {
            'name': self.name,
            'servings': self.servings
        }
    
    @staticmethod
    def _parse_double(value) -> float:
        """Parse a value to a float.
        
        Args:
            value: The value to parse.
            
        Returns:
            The parsed float.
        """
        if value is None:
            return 0.0
        if isinstance(value, int):
            return float(value)
        if isinstance(value, float):
            return value
        if isinstance(value, str):
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0
        return 0.0


@dataclass
class NutritionInfo:
    """Nutrition information model."""
    
    calories: float
    protein: float
    carbs: float
    fat: float
    sodium: float
    fiber: float
    sugar: float
    
    @classmethod
    def from_dict(cls, data: dict) -> 'NutritionInfo':
        """Create a NutritionInfo from a dictionary.
        
        Args:
            data: The dictionary.
            
        Returns:
            The NutritionInfo.
        """
        return cls(
            calories=cls._parse_double(data.get('calories', 0.0)),
            protein=cls._parse_double(data.get('protein', 0.0)),
            carbs=cls._parse_double(data.get('carbs', 0.0)),
            fat=cls._parse_double(data.get('fat', 0.0)),
            sodium=cls._parse_double(data.get('sodium', 0.0)),
            fiber=cls._parse_double(data.get('fiber', 0.0)),
            sugar=cls._parse_double(data.get('sugar', 0.0))
        )
    
    def to_dict(self) -> dict:
        """Convert the NutritionInfo to a dictionary.
        
        Returns:
            The dictionary.
        """
        return {
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'sodium': self.sodium,
            'fiber': self.fiber,
            'sugar': self.sugar
        }
    
    @staticmethod
    def _parse_double(value) -> float:
        """Parse a value to a float.
        
        Args:
            value: The value to parse.
            
        Returns:
            The parsed float.
        """
        if value is None:
            return 0.0
        if isinstance(value, int):
            return float(value)
        if isinstance(value, float):
            return value
        if isinstance(value, str):
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0
        return 0.0


@dataclass
class FoodAnalysisResult:
    """Food analysis result model."""
    
    # Constants for warning messages to ensure consistency
    HIGH_SODIUM_WARNING = "High sodium content"
    HIGH_SUGAR_WARNING = "High sugar content"
    LOW_CONFIDENCE_WARNING = "Analysis confidence is low - nutrition values may be less accurate"
    
    # Thresholds for warnings
    HIGH_SODIUM_THRESHOLD = 500.0  # mg
    HIGH_SUGAR_THRESHOLD = 20.0  # g
    
    id: str
    food_name: str
    ingredients: List[Ingredient]
    nutrition_info: NutritionInfo
    warnings: List[str]
    food_image_url: Optional[str] = None
    timestamp: datetime = None
    is_low_confidence: bool = False
    
    def __post_init__(self):
        """Post initialization."""
        # Generate ID if not provided
        if not hasattr(self, 'id') or not self.id:
            self.id = str(uuid4())
        
        # Set timestamp if not provided
        if not self.timestamp:
            self.timestamp = datetime.now()
    
    @classmethod
    def from_dict(cls, data: dict, id: Optional[str] = None) -> 'FoodAnalysisResult':
        """Create a FoodAnalysisResult from a dictionary.
        
        Args:
            data: The dictionary.
            id: The ID to use.
            
        Returns:
            The FoodAnalysisResult.
        """
        # Parse nutrition info
        nutrition_info = NutritionInfo.from_dict(data.get('nutrition_info', {}))
        
        # Parse ingredients
        ingredients = []
        ingredients_data = data.get('ingredients', [])
        if isinstance(ingredients_data, list):
            for item in ingredients_data:
                if isinstance(item, dict):
                    ingredients.append(Ingredient.from_dict(item))
        
        # Generate warnings if not provided based on thresholds
        warnings = []
        if 'warnings' in data and isinstance(data['warnings'], list):
            warnings = data['warnings']
        else:
            if nutrition_info.sodium > cls.HIGH_SODIUM_THRESHOLD:
                warnings.append(cls.HIGH_SODIUM_WARNING)
            if nutrition_info.sugar > cls.HIGH_SUGAR_THRESHOLD:
                warnings.append(cls.HIGH_SUGAR_WARNING)
        
        # Parse timestamp
        timestamp = datetime.now()
        if 'timestamp' in data:
            try:
                if isinstance(data['timestamp'], int):
                    timestamp = datetime.fromtimestamp(data['timestamp'] / 1000.0)
            except (ValueError, TypeError):
                pass
        
        # Check for low confidence flag
        is_low_confidence = data.get('is_low_confidence', False)
        
        # Create and return the FoodAnalysisResult
        return cls(
            id=id or data.get('id', str(uuid4())),
            food_name=data.get('food_name', ''),
            ingredients=ingredients,
            nutrition_info=nutrition_info,
            warnings=warnings,
            food_image_url=data.get('food_image_url'),
            timestamp=timestamp,
            is_low_confidence=is_low_confidence
        )
    
    def to_dict(self) -> dict:
        """Convert the FoodAnalysisResult to a dictionary.
        
        Returns:
            The dictionary.
        """
        return {
            'id': self.id,
            'food_name': self.food_name,
            'ingredients': [ingredient.to_dict() for ingredient in self.ingredients],
            'nutrition_info': self.nutrition_info.to_dict(),
            'warnings': self.warnings,
            'food_image_url': self.food_image_url,
            'timestamp': int(self.timestamp.timestamp() * 1000),
            'is_low_confidence': self.is_low_confidence
        }
    
    def copy_with(self, **kwargs) -> 'FoodAnalysisResult':
        """Create a copy of the FoodAnalysisResult with updated fields.
        
        Args:
            **kwargs: The fields to update.
            
        Returns:
            The updated FoodAnalysisResult.
        """
        data = self.to_dict()
        data.update(kwargs)
        return self.from_dict(data, id=self.id) 