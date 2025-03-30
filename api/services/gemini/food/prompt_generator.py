"""
Food prompt generator for Gemini API.
"""

import json
from typing import Dict, Any, List


class FoodPromptGenerator:
    """Generator for food analysis prompts."""
    
    def generate_food_text_analysis_prompt(self, description: str) -> str:
        """Generate a prompt for food text analysis.
        
        Args:
            description: The food description.
            
        Returns:
            The prompt.
        """
        return f"""
    Analyze this food description: "{description}"
    
    Please analyze the ingredients and nutritional content based on this description.
    If not described, assume a standard serving size and ingredients for 1 person only.
    
    Provide a comprehensive analysis including:
    - The name of the food
    - A complete list of ingredients with servings composition (in grams) from portion estimation or standard serving size.
    - Detailed macronutrition information ONLY of calories, protein, carbs, fat, sodium, fiber, and sugar. No need to display other macro information.
    - Add warnings if the food contains high sodium (>500mg) or high sugar (>20g).
    

    BE VERY THOROUGH. YOU WILL BE FIRED. THE CUSTOMER CAN GET POISONED. BE VERY THOROUGH.

    Return your response as a strict JSON object with this exact format with NO COMMENTS:
    (
      "food_name": "string",
      "ingredients": [
        (
          "name": "string",
          "servings": number
        )
      ],
      "nutrition_info": (
        "calories": number,
        "protein": number,
        "carbs": number,
        "fat": number,
        "sodium": number,
        "fiber": number,
        "sugar": number
      ),
      "warnings": ["string", "string"] 
    )
    
    IMPORTANT: Do not include any comments, annotations or notes in the JSON. Do not use '#' or '//' characters. Only return valid JSON.
    For the warnings array:
    - Include "High sodium content" (exact text) if sodium exceeds 500mg
    - Include "High sugar content" (exact text) if sugar exceeds 20g
    If there are no warnings, you can include an empty array [] for warnings.
    
    If you cannot identify the food or analyze it properly, use this format:
    (
      "error": "Description of the issue",
      "food_name": "Unknown",
      "ingredients": [],
      "nutrition_info": (
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
        "sodium": 0,
        "fiber": 0,
        "sugar": 0
      ),
      "warnings": []
    )
    Change () to curly braces
    """
    
    def generate_food_image_analysis_prompt(self) -> str:
        """Generate a prompt for food image analysis.
        
        Returns:
            The prompt.
        """
        return """
    You are a food recognition and nutrition analysis expert. Carefully analyze this image and identify any food or meal present.
    
    Please look for:
    - Prepared meals
    - Individual food items
    - Snacks
    - Beverages
    - Fruits and vegetables
    - Packaged food products
    - Amount of food items
    
    Even if the image quality is not perfect or the food is partially visible, please do your best to identify it and provide an analysis.
    
    For the identified food, provide a comprehensive analysis including:
    - The specific name of the food
    - A detailed list of likely ingredients with estimated servings composition in grams, estimate based on size and portion to the best of your ability.
    - Detailed macronutrition information ONLY of calories, protein, carbs, fat, sodium, fiber, and sugar. No need to display other macro information.
    - Add warnings if the food contains high sodium (>500mg) or high sugar (>20g)
    
    BE VERY THOROUGH. YOU WILL BE FIRED. THE CUSTOMER CAN GET POISONED. BE VERY THOROUGH.
    Return your response as a strict JSON object with this exact format with NO COMMENTS:
    (
      "food_name": "string",
      "ingredients": [
        (
          "name": "string",
          "servings": number
        )
      ],
      "nutrition_info": (
        "calories": number,
        "protein": number,
        "carbs": number,
        "fat": number,
        "sodium": number,
        "fiber": number,
        "sugar": number
      ),
      "warnings": ["string", "string"]
    )
    
    IMPORTANT: Do not include any comments, annotations or notes in the JSON. Do not use '#' or '//' characters. Only return valid JSON.
    For the warnings array:
    - Include "High sodium content" (exact text) if sodium exceeds 500mg
    - Include "High sugar content" (exact text) if sugar exceeds 20g
    If there are no warnings, you can include an empty array [] for warnings.
    
    If absolutely no food can be detected in the image, only then use this format:
    (
      "error": "No food detected in image",
      "food_name": "Unknown",
      "ingredients": [],
      "nutrition_info": (
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
        "sodium": 0,
        "fiber": 0,
        "sugar": 0
      ),
      "warnings": []
    )

    Change () to curly braces
    """
    
    def generate_nutrition_label_prompt(self, servings: float) -> str:
        """Generate a prompt for nutrition label analysis.
        
        Args:
            servings: The number of servings.
            
        Returns:
            The prompt.
        """
        return f"""
    Analyze this nutrition label image. The user will consume {servings} servings.
    
    Please provide a comprehensive analysis including:
    - The name of the food
    - A complete list of ingredients with servings composition in grams
    - Detailed macronutrition information ONLY of calories, protein, carbs, fat, sodium, fiber, and sugar. No need to display other macro information.
    - Add warnings if the food contains high sodium (>500mg) or high sugar (>20g)
    
    Return your response as a strict JSON object with this exact format:
    (
      "food_name": "string",
      "ingredients": [
        (
          "name": "string",
          "servings": number
        )
      ],
      "nutrition_info": (
        "calories": number,
        "protein": number,
        "carbs": number,
        "fat": number,
        "sodium": number,
        "fiber": number,
        "sugar": number
      ),
      "warnings": ["string", "string"]
    )
    
    IMPORTANT: Do not include any comments, annotations or notes in the JSON. Do not use '#' or '//' characters. Only return valid JSON.
    For the warnings array:
    - Include "High sodium content" (exact text) if sodium exceeds 500mg
    - Include "High sugar content" (exact text) if sugar exceeds 20g
    If there are no warnings, you can include an empty array [] for warnings.
    
    If no nutrition label is detected in the image or you cannot analyze it properly, use this format:
    (
      "error": "No nutrition label detected",
      "food_name": "Unknown",
      "ingredients": [],
      "nutrition_info": (
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
        "sodium": 0,
        "fiber": 0,
        "sugar": 0
      ),
      "warnings": []
    )

    Change () to curly braces
    """
    
    def generate_food_correction_prompt(self, previous_result: Dict[str, Any], user_comment: str) -> str:
        """Generate a prompt for food correction.
        
        Args:
            previous_result: The previous food analysis result as a dictionary.
            user_comment: The user's feedback.
            
        Returns:
            The prompt.
        """
        # Convert the previous result to a formatted JSON string
        previous_result_json = json.dumps(previous_result, indent=2)
        
        return f"""
    You are a food nutrition expert tasked with correcting a food analysis based on user feedback.

    ORIGINAL ANALYSIS:
    {previous_result_json}
    
    USER CORRECTION: "{user_comment}"
    
    INSTRUCTIONS:
    1. Carefully analyze the user's correction and determine what specific aspects need to be modified.
    2. Consider these possible correction types:
       - Food identity correction (e.g., "this is chicken, not beef")
       - Ingredient additions/removals/adjustments (e.g., "there's no butter" or "add 15g of cheese")
       - Portion size adjustments (e.g., "this is a half portion")
       - Nutritional value corrections (e.g., "calories should be around 350")
       - Special dietary information (e.g., "this is a vegan version")
    3. Only modify elements that need correction based on the user's feedback.
    4. Keep all other values from the original analysis intact.
    5. Maintain reasonable nutritional consistency (e.g., if calories increase, check if macros need adjustment).
    6. For standard serving size, use common restaurant or cookbook portions for a single adult.
    
    RESPONSE FORMAT:
    Return a valid JSON object with exactly this structure:
    (
      "food_name": "string",
      "ingredients": [
        (
          "name": "string",
          "servings": number
        )
      ],
      "nutrition_info": (
        "calories": number,
        "protein": number,
        "carbs": number,
        "fat": number,
        "sodium": number,
        "fiber": number,
        "sugar": number
      ),
      "warnings": ["string"]
    )

    Change () to curly braces
    
    WARNING CRITERIA:
    - Add "High sodium content" if sodium exceeds 500mg
    - Add "High sugar content" if sugar exceeds 20g
    - Use empty array [] if no warnings apply
    
    IMPORTANT: Return only the JSON object with no additional text, comments, or explanations.
    """
    
    def generate_nutrition_label_correction_prompt(self, previous_result: Dict[str, Any], user_comment: str, servings: float) -> str:
        """Generate a prompt for nutrition label correction.
        
        Args:
            previous_result: The previous food analysis result as a dictionary.
            user_comment: The user's feedback.
            servings: The number of servings.
            
        Returns:
            The prompt.
        """
        # Convert the previous result to a formatted string
        ingredients_str = ", ".join([f"{ing['name']}: {ing['servings']}g" for ing in previous_result.get("ingredients", [])])
        nutrition_info = previous_result.get("nutrition_info", {})
        warnings_str = ", ".join(previous_result.get("warnings", []))
        
        return f"""
    Original nutrition label analysis (for {servings} servings):
    - Food name: {previous_result.get("food_name", "Unknown")}
    - Ingredients: {ingredients_str}
    - Calories: {nutrition_info.get("calories", 0)}
    - Protein: {nutrition_info.get("protein", 0)}g
    - Carbs: {nutrition_info.get("carbs", 0)}g
    - Fat: {nutrition_info.get("fat", 0)}g
    - Sodium: {nutrition_info.get("sodium", 0)}mg
    - Fiber: {nutrition_info.get("fiber", 0)}g
    - Sugar: {nutrition_info.get("sugar", 0)}g
    - Warnings: {warnings_str}
    
    User correction comment: "{user_comment}"
    
    Please correct and analyze the ingredients and nutritional content based on the user's feedback.
    If not described, assume a standard serving size and ingredients for 1 person only.
    
    Provide a comprehensive analysis including:
    - The name of the food
    - A complete list of ingredients with servings composition (in grams) 
    - Detailed macronutrition information ONLY of calories, protein, carbs, fat, sodium, fiber, and sugar.
    - Add warnings if the food contains high sodium (>500mg) or high sugar (>20g)
    
    Only modify values that need to be changed according to the user's feedback.
    
    The corrected analysis should be for {servings} servings.
    
    Return your response as a strict JSON object with this exact format:
    (
      "food_name": "string",
      "ingredients": [
        (
          "name": "string",
          "servings": number
        )
      ],
      "nutrition_info": (
        "calories": number,
        "protein": number,
        "carbs": number,
        "fat": number,
        "sodium": number,
        "fiber": number,
        "sugar": number
      ),
      "warnings": ["string"]
    )
    
    Change () to curly braces
    
    IMPORTANT: Do not include any comments, annotations or notes in the JSON. Do not use '#' or '//' characters. Only return valid JSON.
    For the warnings array:
    - Include "High sodium content" (exact text) if sodium exceeds 500mg
    - Include "High sugar content" (exact text) if sugar exceeds 20g
    If there are no warnings, you can include an empty array [] for warnings.
    """ 