"""
Authentication dependencies for FastAPI.
"""

import logging
import os
import json
from typing import Optional, Dict, Any, cast

import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Configure logger
logger = logging.getLogger(__name__)

# Initialize Firebase Admin
try:
    # Check for direct environment variable with credentials JSON content
    firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

    # Check for credentials path
    credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

    if firebase_creds_json:
        # Parse credentials from the environment variable
        logger.info("Initializing Firebase with credentials from environment variable")
        creds_dict = json.loads(firebase_creds_json)
        cred = credentials.Certificate(creds_dict)
    elif credentials_path and os.path.exists(credentials_path):
        # Use credentials from file path
        logger.info(f"Initializing Firebase with credentials from file: {credentials_path}")
        cred = credentials.Certificate(credentials_path)
    else:
        # Try to use individual environment variables
        logger.info("Initializing Firebase with individual credential environment variables")

        # Required fields for a service account
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace(
            "\\n", "\n"
        )  # Handle escaped newlines
        client_email = os.getenv("FIREBASE_CLIENT_EMAIL")

        if project_id and private_key and client_email:
            creds_dict = {
                "type": os.getenv("FIREBASE_ACCOUNT_TYPE", "service_account"),
                "project_id": project_id,
                "private_key": private_key,
                "client_email": client_email,
                "client_id": os.getenv("FIREBASE_CLIENT_ID", ""),
                "auth_uri": os.getenv(
                    "FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"
                ),
                "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
                "auth_provider_x509_cert_url": os.getenv(
                    "FIREBASE_AUTH_PROVIDER_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs"
                ),
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL", ""),
            }
            cred = credentials.Certificate(creds_dict)
        else:
            # As a last resort, try local file
            logger.warning("No Firebase credentials found in environment, trying local file")
            cred = credentials.Certificate("firebase-credentials.json")

    # Initialize the app
    firebase_admin.initialize_app(cred)
    logger.info("Firebase Admin initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Firebase Admin: {str(e)}")

# Bearer token authentication scheme
security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[Any, Any]:
    """
    Verify the JWT token from Firebase.

    Args:
        credentials: The HTTP authorization credentials.

    Returns:
        The decoded token claims.

    Raises:
        HTTPException: If the token is invalid.
    """
    token = credentials.credentials
    try:
        # Verify the token
        decoded_token = auth.verify_id_token(token)
        logger.info(f"Token verified for user: {decoded_token.get('uid')}")
        return cast(Dict[Any, Any], decoded_token)
    except Exception as e:
        logger.error(f"Invalid token: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid authentication credentials: {str(e)}")


async def get_current_user(token: dict = Depends(verify_token)) -> dict:
    """
    Get the current user from the verified token.

    Args:
        token: The verified token claims.

    Returns:
        The user information.
    """
    # Extract user information from token
    uid = token.get("uid")
    email = token.get("email")
    name = token.get("name")

    # Return user info
    return {"uid": uid, "email": email, "name": name}


# Optional token verification that doesn't raise an exception for unauthenticated routes
async def optional_verify_token(request: Request) -> Optional[Dict[Any, Any]]:
    """
    Optionally verify the JWT token from Firebase.

    Args:
        request: The HTTP request.

    Returns:
        The decoded token claims or None if no token or invalid token.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    try:
        # Verify the token
        decoded_token = auth.verify_id_token(token)
        return cast(Dict[Any, Any], decoded_token)
    except Exception as e:
        logger.warning(f"Invalid token in optional verification: {str(e)}")
        return None
