# PockEat API Tests

This directory contains tests for the PockEat API, providing comprehensive test coverage for all components of the application.

## Test Structure

The tests are organized into the following directories:

- `unit/`: Unit tests for individual components
  - `models/`: Tests for data models (food_analysis, exercise_analysis)
  - `dependencies/`: Tests for auth dependency
  - `services/`: Tests for services (gemini_service, base_service, food_service, exercise_service)
- `middleware/`: Tests for the auth middleware
- `integration/`: Integration tests for API routes

## Running Tests

To run all tests:

```bash
pytest
```

To run a specific test file:

```bash
pytest tests/unit/services/test_gemini_service.py
```

To run tests in a specific directory:

```bash
pytest tests/unit/models/
```

## Coverage Report

To generate a coverage report:

```bash
pytest --cov=api
```

For a detailed HTML report:

```bash
pytest --cov=api --cov-report=html
```

View the HTML report by opening `htmlcov/index.html` in a browser.

## Test Configuration

The `pytest.ini` file contains configuration settings for running tests. These settings include:

- Test discovery patterns
- Verbosity levels
- Coverage options

## Dependencies

All test dependencies are listed in `requirements.txt`. Install them with:

```bash
pip install -r requirements.txt
```

## Adding New Tests

When adding new tests:

1. Follow the naming convention: `test_*.py` for files and `test_*` for functions
2. Include both positive and negative test cases
3. Use mocks for external services (Firebase, Gemini API)
4. Aim for 100% code coverage
5. Use fixtures from `conftest.py` for common test setup
6. For async functions, use the `@pytest.mark.asyncio` decorator

## Service Tests

The service tests extensively cover:

1. **Base Service Tests** (`test_base_service.py`):
   - LangChain integration
   - Image processing
   - Error handling
   - API interactions

2. **Gemini Service Tests** (`test_gemini_service.py`):
   - Main service initialization and configuration
   - Integration with specialized services
   - Error propagation
   
3. **Food Analysis Service Tests** (`test_food_service.py`):
   - Text-based food analysis
   - Image-based food analysis
   - Nutrition label analysis
   - User correction functionality
   
4. **Exercise Analysis Service Tests** (`test_exercise_service.py`):
   - Exercise analysis with and without user weight
   - User correction functionality
   - Prompt generation and response parsing 