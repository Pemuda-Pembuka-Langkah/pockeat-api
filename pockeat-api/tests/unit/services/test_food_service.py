def test_generate_food_image_analysis_prompt(self, mock_env):
    """Test generating food image analysis prompt."""
    with patch('api.services.gemini.food_service.BaseLangChainService'):
        service = FoodAnalysisService()

        prompt = service._generate_food_image_analysis_prompt()

        assert "food recognition" in prompt.lower()
        assert "nutrition analysis" in prompt.lower()