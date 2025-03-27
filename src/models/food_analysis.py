"""
Models for food analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from uuid import uuid4


@dataclass
class Ingredient:
    """Ingredient model."""
    
    name: str
    servings: float  # in grams


@dataclass
class NutritionInfo:
    """Nutrition information model."""
    
    calories: float = 0
    protein: float = 0
    carbs: float = 0
    fat: float = 0
    sodium: float = 0
    fiber: float = 0
    sugar: float = 0


@dataclass
class FoodAnalysisResult:
    """Food analysis result model."""
    
    id: str
    food_name: str
    ingredients: List[Ingredient]
    nutrition_info: NutritionInfo
    warnings: List[str]
    error: Optional[str] = None  # Added error field
    timestamp: datetime = None
    
    def __post_init__(self):
        """Post initialization."""
        # Generate ID if not provided
        if not hasattr(self, 'id') or not self.id:
            self.id = str(uuid4())
        
        # Set timestamp if not provided
        if not self.timestamp:
            self.timestamp = datetime.now()
        
        # Add standard warnings based on nutrition values if not already present
        if self.nutrition_info and not self.error:
            warnings_set = set(self.warnings)
            
            if self.nutrition_info.sodium > 500 and "High sodium content" not in warnings_set:
                warnings_set.add("High sodium content")
            
            if self.nutrition_info.sugar > 20 and "High sugar content" not in warnings_set:
                warnings_set.add("High sugar content")
            
            self.warnings = list(warnings_set)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], id: Optional[str] = None) -> 'FoodAnalysisResult':
        """Create a FoodAnalysisResult from a dictionary.
        
        Args:
            data: The dictionary.
            id: The ID to use (optional).
            
        Returns:
            The FoodAnalysisResult.
        """
        # Parse timestamp if present
        timestamp = datetime.now()
        if 'timestamp' in data:
            try:
                if isinstance(data['timestamp'], int):
                    timestamp = datetime.fromtimestamp(data['timestamp'] / 1000.0)
            except (ValueError, TypeError):
                pass
        
        # Extract error if present
        error = data.get('error')
        
        # Parse ingredients
        ingredients = []
        if 'ingredients' in data and isinstance(data['ingredients'], list):
            for ing_data in data['ingredients']:
                if isinstance(ing_data, dict):
                    name = ing_data.get('name', 'Unknown ingredient')
                    servings = float(ing_data.get('servings', 0))
                    ingredients.append(Ingredient(name=name, servings=servings))
        
        # Parse nutrition info
        nutrition_info = NutritionInfo()
        if 'nutrition_info' in data and isinstance(data['nutrition_info'], dict):
            nutrition_data = data['nutrition_info']
            nutrition_info = NutritionInfo(
                calories=float(nutrition_data.get('calories', 0)),
                protein=float(nutrition_data.get('protein', 0)),
                carbs=float(nutrition_data.get('carbs', 0)),
                fat=float(nutrition_data.get('fat', 0)),
                sodium=float(nutrition_data.get('sodium', 0)),
                fiber=float(nutrition_data.get('fiber', 0)),
                sugar=float(nutrition_data.get('sugar', 0))
            )
        
        # Extract warnings
        warnings = []
        if 'warnings' in data and isinstance(data['warnings'], list):
            warnings = [str(w) for w in data['warnings']]
        
        # Create and return the result
        return cls(
            id=id or data.get('id', str(uuid4())),
            food_name=data.get('food_name', 'Unknown'),
            ingredients=ingredients,
            nutrition_info=nutrition_info,
            warnings=warnings,
            error=error,
            timestamp=timestamp
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the FoodAnalysisResult to a dictionary.
        
        Returns:
            The dictionary.
        """
        result = {
            'id': self.id,
            'food_name': self.food_name,
            'ingredients': [{'name': i.name, 'servings': i.servings} for i in self.ingredients],
            'nutrition_info': {
                'calories': self.nutrition_info.calories,
                'protein': self.nutrition_info.protein,
                'carbs': self.nutrition_info.carbs,
                'fat': self.nutrition_info.fat,
                'sodium': self.nutrition_info.sodium,
                'fiber': self.nutrition_info.fiber,
                'sugar': self.nutrition_info.sugar
            },
            'warnings': self.warnings,
            'timestamp': int(self.timestamp.timestamp() * 1000)
        }
        
        # Include error field only if it has a value
        if self.error:
            result['error'] = self.error
            
        return result
    
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