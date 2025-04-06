"""
API routes for PockEat API.
"""

import logging
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse

from api.services.gemini_service import GeminiService
from api.services.gemini.exceptions import GeminiServiceException
from api.models.food_analysis import (
    FoodAnalysisResult, 
    FoodAnalysisRequest, 
    FoodCorrectionRequest
)
from api.models.exercise_analysis import (
    ExerciseAnalysisResult,
    ExerciseAnalysisRequest, 
    ExerciseCorrectionRequest
)
from api.dependencies.auth import get_current_user, verify_token, optional_verify_token

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize service
gemini_service = None

try:
    gemini_service = GeminiService()
except Exception as e:  # pragma: no cover
    logger.error(f"Failed to initialize Gemini service: {str(e)}")


# Dependency to get Gemini service
async def get_gemini_service() -> GeminiService:
    """Get Gemini service."""
    if gemini_service is None:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini service is unavailable"
        )
    return gemini_service


@router.get("/health", summary="Health check", tags=["Health"])
async def health_check(gemini: GeminiService = Depends(get_gemini_service)):
    """Health check endpoint."""
    is_gemini_available = await gemini.check_health()
    
    return {
        "status": "healthy" if is_gemini_available else "degraded",
        "message": "API is running" + ("" if is_gemini_available else ", but Gemini service is unavailable")
    }


@router.post(
    "/food/analyze/text", 
    response_model=FoodAnalysisResult, 
    summary="Analyze food from text", 
    tags=["Food"]
)
async def analyze_food_by_text(
    request: FoodAnalysisRequest,
    gemini: GeminiService = Depends(get_gemini_service)
):
    """Analyze food from text description."""
    logger.info(f"Received food analysis request: {request.description}")
    try:
        result = await gemini.analyze_food_by_text(request.description)
        print(f"Food analysis result: {result}")
        return result
    except GeminiServiceException as e:
        raise HTTPException(  # pragma: no cover
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Error in analyze_food_by_text: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze food: {str(e)}"
        )


@router.post(
    "/food/analyze/image", 
    response_model=FoodAnalysisResult, 
    summary="Analyze food from image", 
    tags=["Food"]
)
async def analyze_food_by_image(
    image: UploadFile = File(...),
    gemini: GeminiService = Depends(get_gemini_service)
):
    """Analyze food from image."""
    try:
        result = await gemini.analyze_food_by_image(image.file)
        return result
    except GeminiServiceException as e:  # pragma: no cover
        # Use the error structure from the returned object
        return JSONResponse(  # pragma: no cover
            status_code=e.status_code,
            content={
                "error": e.message,
                "food_name": "Unknown",
                "ingredients": [],
                "nutrition_info": {
                    "calories": 0,
                    "protein": 0,
                    "carbs": 0,
                    "fat": 0,
                    "sodium": 0,
                    "fiber": 0,
                    "sugar": 0
                }
            }
        )
    except Exception as e:  # pragma: no cover
        logger.error(f"Error in analyze_food_by_image: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": f"Failed to analyze food image: {str(e)}",
                "food_name": "Unknown",
                "ingredients": [],
                "nutrition_info": {
                    "calories": 0,
                    "protein": 0,
                    "carbs": 0,
                    "fat": 0,
                    "sodium": 0,
                    "fiber": 0,
                    "sugar": 0
                }
            }
        )


@router.post(
    "/food/analyze/nutrition-label", 
    response_model=FoodAnalysisResult, 
    summary="Analyze nutrition label", 
    tags=["Food"]
)
async def analyze_nutrition_label(
    image: UploadFile = File(...),
    servings: float = Form(1.0),
    gemini: GeminiService = Depends(get_gemini_service)
):
    """Analyze nutrition label from image."""
    try:
        result = await gemini.analyze_nutrition_label(image.file, servings)
        return result
    except GeminiServiceException as e:  # pragma: no cover
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:  # pragma: no cover
        logger.error(f"Error in analyze_nutrition_label: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze nutrition label: {str(e)}"
        )


@router.post(
    "/exercise/analyze", 
    response_model=ExerciseAnalysisResult, 
    summary="Analyze exercise", 
    tags=["Exercise"]
)
async def analyze_exercise(
    request: ExerciseAnalysisRequest,
    gemini: GeminiService = Depends(get_gemini_service)
):
    """Analyze exercise from description."""
    try:
        result = await gemini.analyze_exercise(request.description, request.user_weight_kg)
        return result
    except GeminiServiceException as e:  # pragma: no cover
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:  # pragma: no cover
        logger.error(f"Error in analyze_exercise: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze exercise: {str(e)}"
        )


@router.post(
    "/food/correct/text", 
    response_model=FoodAnalysisResult, 
    summary="Correct food text analysis", 
    tags=["Food"]
)
async def correct_food_text_analysis(
    request: FoodCorrectionRequest,
    gemini: GeminiService = Depends(get_gemini_service)
):
    """Correct food text analysis."""
    try:
        result = await gemini.correct_food_analysis(request.previous_result, request.user_comment)
        return result
    except GeminiServiceException as e:  # pragma: no cover
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:  # pragma: no cover
        logger.error(f"Error in correct_food_text_analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )


@router.post(
    "/exercise/correct", 
    response_model=ExerciseAnalysisResult, 
    summary="Correct exercise analysis", 
    tags=["Exercise"]
)
async def correct_exercise_analysis(
    request: ExerciseCorrectionRequest,
    gemini: GeminiService = Depends(get_gemini_service)
):
    """Correct exercise analysis."""
    try:
        result = await gemini.correct_exercise_analysis(request.previous_result, request.user_comment)
        return result
    except GeminiServiceException as e:  # pragma: no cover
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:  # pragma: no cover
        logger.error(f"Error in correct_exercise_analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )


@router.get("/debug-env", tags=["Debug"])
async def debug_env():  # pragma: no cover
    """Debug endpoint for environment variables."""
    return {
        "has_key": bool(os.getenv("GOOGLE_API_KEY")),
        "env_vars": list(os.environ.keys())
    }


@router.get(
    "/user/profile", 
    summary="Get user profile", 
    tags=["User"]
)
async def get_user_profile(user: dict = Depends(get_current_user)):  # pragma: no cover
    """Get the user profile for the authenticated user."""
    return {
        "uid": user.get("uid"),
        "email": user.get("email"),
        "name": user.get("name"),
        "message": "Successfully authenticated with Firebase"
    }

@router.get(
    "/protected-example",
    summary="Protected route example",
    tags=["Examples"]
)
async def protected_example(token: dict = Depends(verify_token)):  # pragma: no cover
    """Example of a protected route that requires authentication."""
    return {
        "message": "This is a protected endpoint",
        "user_id": token.get("uid"),
        "email": token.get("email")
    }

@router.get(
    "/optional-auth-example",
    summary="Optional authentication example",
    tags=["Examples"]
)
async def optional_auth_example(request: Request):  # pragma: no cover
    """Example of a route with optional authentication."""
    user = await optional_verify_token(request)
    
    if user:
        return {
            "message": "Authenticated user",
            "user_id": user.get("uid")
        }
    else:
        return {
            "message": "Unauthenticated user"
        } 