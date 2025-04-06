"""
Tests for the food analysis models.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from api.models.food_analysis import (
    Ingredient, 
    NutritionInfo, 
    FoodAnalysisResult, 
    FoodAnalysisRequest,
    FoodCorrectionRequest
)

class TestIngredient:
    """Tests for the Ingredient model."""
    
    def test_ingredient_creation(self):
        """Test creating an ingredient."""
        ingredient = Ingredient(name="Test Ingredient", servings=100)
        assert ingredient.name == "Test Ingredient"
        assert ingredient.servings == 100
    
    def test_ingredient_validation(self):
        """Test ingredient validation."""
        # Missing name should raise error
        with pytest.raises(Exception):
            Ingredient(servings=100)
        
        # Missing servings should default to 0
        ingredient = Ingredient(name="Test")
        assert ingredient.name == "Test"
        assert ingredient.servings == 0

class TestNutritionInfo:
    """Tests for the NutritionInfo model."""
    
    def test_nutrition_info_creation(self):
        """Test creating nutrition info with full values."""
        nutrition = NutritionInfo(
            calories=200,
            protein=10,
            carbs=20,
            fat=5,
            sodium=100,
            fiber=2,
            sugar=5
        )
        assert nutrition.calories == 200
        assert nutrition.protein == 10
        assert nutrition.carbs == 20
        assert nutrition.fat == 5
        assert nutrition.sodium == 100
        assert nutrition.fiber == 2
        assert nutrition.sugar == 5
    
    def test_nutrition_info_defaults(self):
        """Test default values for nutrition info."""
        nutrition = NutritionInfo()
        assert nutrition.calories == 0
        assert nutrition.protein == 0
        assert nutrition.carbs == 0
        assert nutrition.fat == 0
        assert nutrition.sodium == 0
        assert nutrition.fiber == 0
        assert nutrition.sugar == 0
    
    def test_nutrition_info_partial(self):
        """Test creating nutrition info with partial values."""
        nutrition = NutritionInfo(calories=200, protein=10)
        assert nutrition.calories == 200
        assert nutrition.protein == 10
        assert nutrition.carbs == 0  # Default
        assert nutrition.fat == 0  # Default

class TestFoodAnalysisResult:
    """Tests for the FoodAnalysisResult model."""
    
    def test_food_analysis_result_creation(self):
        """Test creating a food analysis result."""
        nutrition = NutritionInfo(calories=200, protein=10)
        ingredients = [Ingredient(name="Ingredient 1", servings=100)]
        
        result = FoodAnalysisResult(
            food_name="Test Food",
            ingredients=ingredients,
            nutrition_info=nutrition
        )
        
        assert result.food_name == "Test Food"
        assert len(result.ingredients) == 1
        assert result.ingredients[0].name == "Ingredient 1"
        assert result.nutrition_info.calories == 200
        assert result.error is None
        assert isinstance(result.timestamp, datetime)
        
        # ID should be auto-generated
        assert result.id is not None
    
    def test_food_analysis_result_defaults(self):
        """Test default values for food analysis result."""
        result = FoodAnalysisResult(food_name="Test Food")
        
        assert result.food_name == "Test Food"
        assert result.ingredients == []
        assert isinstance(result.nutrition_info, NutritionInfo)
        assert result.error is None
    
    def test_food_analysis_with_error(self):
        """Test food analysis result with error."""
        result = FoodAnalysisResult(
            food_name="Unknown",
            error="Failed to analyze food"
        )
        
        assert result.food_name == "Unknown"
        assert result.error == "Failed to analyze food"

class TestFoodAnalysisRequest:
    """Tests for the FoodAnalysisRequest model."""
    
    def test_food_analysis_request_creation(self):
        """Test creating a food analysis request."""
        request = FoodAnalysisRequest(description="A grilled chicken sandwich")
        assert request.description == "A grilled chicken sandwich"
    
    def test_food_analysis_request_validation(self):
        """Test request validation."""
        # Missing description should raise error
        with pytest.raises(Exception):
            FoodAnalysisRequest()

class TestFoodCorrectionRequest:
    """Tests for the FoodCorrectionRequest model."""
    
    def test_food_correction_request_creation(self):
        """Test creating a food correction request."""
        previous_result = FoodAnalysisResult(food_name="Test Food")
        
        request = FoodCorrectionRequest(
            previous_result=previous_result,
            user_comment="Please correct this",
            servings=2.0
        )
        
        assert request.previous_result == previous_result
        assert request.user_comment == "Please correct this"
        assert request.servings == 2.0
    
    def test_food_correction_request_defaults(self):
        """Test defaults for food correction request."""
        previous_result = FoodAnalysisResult(food_name="Test Food")
        
        request = FoodCorrectionRequest(
            previous_result=previous_result,
            user_comment="Please correct this"
        )
        
        assert request.servings == 1.0  # Default value
    
    def test_food_correction_request_validation(self):
        """Test request validation."""
        # Missing previous_result should raise error
        with pytest.raises(Exception):
            FoodCorrectionRequest(user_comment="Please correct this")
        
        # Missing user_comment should raise error
        previous_result = FoodAnalysisResult(food_name="Test Food")
        with pytest.raises(Exception):
            FoodCorrectionRequest(previous_result=previous_result) 