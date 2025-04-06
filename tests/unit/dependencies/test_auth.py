"""
Tests for the auth dependencies.
"""

import pytest
import os
import json
from unittest.mock import patch, MagicMock
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials

from api.dependencies.auth import (
    verify_token,
    get_current_user,
    optional_verify_token
)

class TestAuthDependencies:
    """Tests for auth dependencies."""
    
    @pytest.fixture
    def mock_request(self):
        """Create a mock request object."""
        mock_req = MagicMock(spec=Request)
        mock_req.headers = {"Authorization": "Bearer valid-token"}
        return mock_req
    
    @pytest.fixture
    def mock_verify_token_result(self):
        """Mock result from verify_token."""
        return {
            "uid": "test-uid",
            "email": "test@example.com",
            "name": "Test User"
        }
    
    @pytest.fixture
    def mock_credentials(self):
        """Create mock credentials."""
        return HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token")
    
    @pytest.mark.asyncio
    async def test_verify_token_success(self, mock_credentials, mock_firebase_admin):
        """Test successful token verification."""
        # Set up mock return value
        expected_result = {
            "uid": "test-uid",
            "email": "test@example.com",
            "name": "Test User" 
        }
        mock_firebase_admin.return_value = expected_result
        
        # Call the function
        result = await verify_token(mock_credentials)
        
        # Check results
        assert result == expected_result
        mock_firebase_admin.assert_called_once_with("valid-token")
    
    @pytest.mark.asyncio
    async def test_verify_token_failure(self, mock_credentials, mock_firebase_admin):
        """Test failed token verification."""
        # Set up mock to raise exception
        mock_firebase_admin.side_effect = Exception("Invalid token")
        
        # Call the function and check for exception
        with pytest.raises(HTTPException) as exc_info:
            await verify_token(mock_credentials)
        
        # Check exception details
        assert exc_info.value.status_code == 401
        assert "Invalid authentication credentials" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, mock_verify_token_result):
        """Test get_current_user function."""
        # Call the function
        user = await get_current_user(mock_verify_token_result)
        
        # Check result
        assert user == {
            "uid": "test-uid",
            "email": "test@example.com", 
            "name": "Test User"
        }
    
    @pytest.mark.asyncio
    async def test_optional_verify_token_with_valid_token(self, mock_request, mock_firebase_admin):
        """Test optional_verify_token with a valid token."""
        # Set up mock return value
        expected_result = {
            "uid": "test-uid",
            "email": "test@example.com"
        }
        mock_firebase_admin.return_value = expected_result
        
        # Call the function
        result = await optional_verify_token(mock_request)
        
        # Check results
        assert result == expected_result
        mock_firebase_admin.assert_called_once_with("valid-token")
    
    @pytest.mark.asyncio
    async def test_optional_verify_token_without_auth_header(self):
        """Test optional_verify_token without any auth header."""
        # Create a request with no Authorization header
        mock_req = MagicMock(spec=Request)
        mock_req.headers = {}
        
        # Call the function
        result = await optional_verify_token(mock_req)
        
        # Check results
        assert result is None
    
    @pytest.mark.asyncio
    async def test_optional_verify_token_with_invalid_scheme(self):
        """Test optional_verify_token with an invalid auth scheme."""
        # Create a request with invalid Authorization header
        mock_req = MagicMock(spec=Request)
        mock_req.headers = {"Authorization": "Basic dXNlcjpwYXNz"}
        
        # Call the function
        result = await optional_verify_token(mock_req)
        
        # Check results
        assert result is None
    
    @pytest.mark.asyncio
    async def test_optional_verify_token_with_invalid_token(self, mock_request, mock_firebase_admin):
        """Test optional_verify_token with an invalid token."""
        # Set up mock to raise exception
        mock_firebase_admin.side_effect = Exception("Invalid token")
        
        # Call the function
        result = await optional_verify_token(mock_request)
        
        # Check results
        assert result is None
    
    @patch("firebase_admin.initialize_app")
    @patch("firebase_admin.credentials.Certificate")
    def test_firebase_initialization_with_env_json(self, mock_certificate, mock_init_app):
        """Test Firebase initialization with JSON from environment variable."""
        # Create test data
        test_creds = {
            "type": "service_account",
            "project_id": "test-project",
            "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n",
            "client_email": "test@example.com"
        }
        
        # Mock environment variables
        with patch.dict(os.environ, {"FIREBASE_CREDENTIALS_JSON": json.dumps(test_creds)}):
            # Force reload the module to trigger initialization with our mocked environment
            import importlib
            import api.dependencies.auth
            importlib.reload(api.dependencies.auth)
            
            # Check that Certificate was called with the right arguments
            mock_certificate.assert_called_once()
            # The first argument should be our test credentials
            assert mock_certificate.call_args[0][0] == test_creds
            
            # Check that initialize_app was called
            mock_init_app.assert_called_once()
    
    @patch("firebase_admin.initialize_app")
    @patch("firebase_admin.credentials.Certificate")
    def test_firebase_initialization_with_individual_vars(self, mock_certificate, mock_init_app):
        """Test Firebase initialization with individual environment variables."""
        # Mock environment variables
        with patch.dict(os.environ, {
            "FIREBASE_PROJECT_ID": "test-project",
            "FIREBASE_PRIVATE_KEY": "-----BEGIN PRIVATE KEY-----\\ntest\\n-----END PRIVATE KEY-----\\n",
            "FIREBASE_CLIENT_EMAIL": "test@example.com"
        }, clear=True):  # Clear existing env vars to ensure clean test
            # Force reload the module to trigger initialization
            import importlib
            import api.dependencies.auth
            importlib.reload(api.dependencies.auth)
            
            # Check that Certificate was called
            mock_certificate.assert_called_once()
            
            # Create expected certificate data
            expected_cert_data = {
                "type": "service_account",
                "project_id": "test-project",
                "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n",
                "client_email": "test@example.com",
                "client_id": "",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": ""
            }
            
            # Compare with what was actually passed to Certificate
            cert_data = mock_certificate.call_args[0][0]
            
            # Because actual data might contain additional fields, we'll check that 
            # our expected values are a subset of the actual data
            for key, value in expected_cert_data.items():
                assert key in cert_data, f"Missing expected key: {key}"
                assert cert_data[key] == value, f"Value mismatch for {key}: expected={value}, actual={cert_data[key]}"
            
            # Check that initialize_app was called
            mock_init_app.assert_called_once()
    
    @patch("firebase_admin.initialize_app")
    @patch("firebase_admin.credentials.Certificate")
    @patch("os.path.exists")
    def test_firebase_initialization_with_credentials_path(self, mock_exists, mock_certificate, mock_init_app):
        """Test Firebase initialization with credentials path."""
        # Mock environment variables and file existence
        credentials_path = "/path/to/credentials.json"
        mock_exists.return_value = True
        
        with patch.dict(os.environ, {"FIREBASE_CREDENTIALS_PATH": credentials_path}, clear=True):
            # Force reload the module to trigger initialization
            import importlib
            import api.dependencies.auth
            importlib.reload(api.dependencies.auth)
            
            # Check that Certificate was called with the correct path
            mock_certificate.assert_called_once_with(credentials_path)
            
            # Check that initialize_app was called
            mock_init_app.assert_called_once()
    
    @patch("firebase_admin.initialize_app")
    @patch("firebase_admin.credentials.Certificate")
    def test_firebase_initialization_fallback(self, mock_certificate, mock_init_app):
        """Test Firebase initialization fallback to default file."""
        # Make sure no environment variables are set
        with patch.dict(os.environ, {}, clear=True):
            # Force reload the module to trigger initialization
            import importlib
            import api.dependencies.auth
            importlib.reload(api.dependencies.auth)
            
            # Check that Certificate was called with default path
            mock_certificate.assert_called_once_with("firebase-credentials.json")
            
            # Check that initialize_app was called
            mock_init_app.assert_called_once()
    
    @patch("firebase_admin.initialize_app")
    @patch("firebase_admin.credentials.Certificate")
    def test_firebase_initialization_error_handling(self, mock_certificate, mock_init_app):
        """Test Firebase initialization error handling."""
        # Make Certificate raise an exception
        mock_certificate.side_effect = Exception("Test error")
        
        # Force reload the module to trigger initialization
        import importlib
        import api.dependencies.auth
        importlib.reload(api.dependencies.auth)
        
        # Initialization should fail gracefully
        mock_certificate.assert_called_once()
        mock_init_app.assert_not_called() 