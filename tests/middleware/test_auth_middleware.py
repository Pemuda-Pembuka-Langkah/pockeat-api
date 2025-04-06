"""
Tests for the authentication middleware.
"""

import os
import sys
import pytest
from fastapi import FastAPI, Depends, Response
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path so we can import from main.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from main import AuthMiddleware, app
from api.dependencies.auth import verify_token, get_current_user

# Create a simple test app with auth middleware
test_app = FastAPI()
test_app.add_middleware(AuthMiddleware)

@test_app.get("/protected")
async def protected_route():
    return {"message": "This is protected"}

@test_app.get("/user-info")
async def user_info(user: dict = Depends(get_current_user)):
    return user

class TestAuthMiddleware:
    """Tests for authentication middleware."""
    
    def test_docs_paths_no_auth_required(self, test_client):
        """Test that documentation paths don't require authentication."""
        # Temporarily enable auth for this test
        with patch.dict(os.environ, {"GLOBAL_AUTH_ENABLED": "true"}):
            test_client = TestClient(app)
            for path in ["/docs", "/redoc", "/openapi.json"]:
                response = test_client.get(path)
                assert response.status_code != 401, f"Documentation path {path} should not require auth"
    
    def test_protected_route_without_token(self, test_client):
        """Test that protected routes require authentication."""
        # Temporarily enable auth for this test
        with patch.dict(os.environ, {"GLOBAL_AUTH_ENABLED": "true"}):
            test_client = TestClient(app)
            response = test_client.get("/")
            assert response.status_code == 401
            assert response.json() == {"detail": "Authentication required"}
            
            response = test_client.get("/health")
            assert response.status_code == 401
            assert response.json() == {"detail": "Authentication required"}
    
    def test_protected_route_with_valid_token(self, test_client_with_mock_firebase, auth_headers):
        """Test that protected routes work with valid token."""
        # Temporarily enable auth for this test
        with patch.dict(os.environ, {"GLOBAL_AUTH_ENABLED": "true"}):
            test_client = TestClient(app)
            response = test_client.get("/", headers=auth_headers)
            assert response.status_code == 200
            assert "status" in response.json()
            
            response = test_client.get("/health", headers=auth_headers)
            assert response.status_code == 200
            assert "status" in response.json()
    
    def test_invalid_token(self, test_client_with_mock_firebase, mock_firebase_admin, invalid_auth_headers):
        """Test that invalid tokens are rejected."""
        # Temporarily enable auth for this test
        with patch.dict(os.environ, {"GLOBAL_AUTH_ENABLED": "true"}):
            # Configure mock to raise for invalid token
            mock_firebase_admin.side_effect = Exception("Invalid token")
            
            test_client = TestClient(app)
            response = test_client.get("/", headers=invalid_auth_headers)
            assert response.status_code == 401
            assert response.json() == {"detail": "Authentication required"}
    
    def test_auth_disabled(self, test_client):
        """Test that authentication can be disabled via environment variable."""
        with patch.dict(os.environ, {"GLOBAL_AUTH_ENABLED": "false"}):
            # We need to reload app to pick up env var change
            test_client = TestClient(app)
            response = test_client.get("/")
            assert response.status_code == 200
            assert "status" in response.json()
    
    def test_options_request_bypass_auth(self, test_client):
        """Test that OPTIONS requests bypass authentication (for CORS)."""
        # Temporarily enable auth for this test
        with patch.dict(os.environ, {"GLOBAL_AUTH_ENABLED": "true"}):
            test_client = TestClient(app)
            response = test_client.options("/")
            assert response.status_code != 401, "OPTIONS requests should bypass auth for CORS"
    
    def test_user_info_from_token(self, test_client_with_mock_firebase, auth_headers):
        """Test that user info can be extracted from token."""
        # Temporarily enable auth for this test
        with patch.dict(os.environ, {"GLOBAL_AUTH_ENABLED": "true"}):
            with patch("api.dependencies.auth.verify_token") as mock_verify:
                # Configure mock to return a specific user that matches what's returned by the conftest
                mock_verify.return_value = {
                    "uid": "test-user-id", 
                    "email": "test@example.com",
                    "name": "Test User"
                }
                
                # Create a client that uses our app with the route
                test_app_client = TestClient(test_app)
                response = test_app_client.get("/user-info", headers=auth_headers)
                
                assert response.status_code == 200
                assert response.json() == {
                    "uid": "test-user-id",
                    "email": "test@example.com",
                    "name": "Test User"
                } 