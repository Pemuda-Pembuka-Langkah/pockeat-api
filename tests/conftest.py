"""
Pytest fixtures for testing.
"""
import pytest
from app import create_app

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app("testing")
    
    # Setup test environment
    app.config.update({
        "TESTING": True,
    })
    
    # Other setup can go here
    
    yield app
    
    # Clean up / reset resources here

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner() 