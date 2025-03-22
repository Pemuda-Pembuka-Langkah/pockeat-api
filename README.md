# PockEat API

A Flask-based REST API for food and exercise analysis using Google's Gemini API. This backend service is designed to work with the PockEat mobile app, providing food and exercise analysis capabilities.

## Features

- **Food Analysis**:
  - Analyze food from text descriptions
  - Analyze food from images
  - Analyze nutrition labels
  - Correct food analysis based on user feedback

- **Exercise Analysis**:
  - Analyze exercise descriptions
  - Correct exercise analysis based on user feedback

## Setup

### Prerequisites

- Python 3.9+
- A Google Gemini API key (https://ai.google.dev/)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pockeat-api.git
   cd pockeat-api
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following variables:
   ```
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   GEMINI_API_KEY=your-gemini-api-key
   ```

### Running the Application

Run the application with:
```bash
python run.py
```

The API will be available at `http://localhost:5000`.

## API Endpoints

### Food Analysis

- **Analyze Food Text Description**:
  ```
  POST /api/v1/food/text
  Content-Type: application/json
  
  {
    "food_description": "A grilled chicken sandwich with lettuce, tomato, and mayo"
  }
  ```

- **Analyze Food Image**:
  ```
  POST /api/v1/food/analyze
  Content-Type: multipart/form-data
  
  image: [file]
  ```

- **Analyze Nutrition Label**:
  ```
  POST /api/v1/food/nutrition-label
  Content-Type: multipart/form-data
  
  image: [file]
  servings: 1.0
  ```

- **Correct Food Analysis**:
  ```
  POST /api/v1/food/correct
  Content-Type: application/json
  
  {
    "food_entry": {...},  // Previous analysis result
    "user_correction": "The chicken is grilled, not fried"
  }
  ```

### Exercise Analysis

- **Analyze Exercise**:
  ```
  POST /api/v1/exercise/analyze
  Content-Type: application/json
  
  {
    "description": "30 minutes of running at 6mph",
    "user_weight": 70.5  // Optional, in kg
  }
  ```

- **Correct Exercise Analysis**:
  ```
  POST /api/v1/exercise/correct
  Content-Type: application/json
  
  {
    "exercise_entry": {...},  // Previous analysis result
    "user_correction": "I ran for 45 minutes, not 30"
  }
  ```

## Development

### Project Structure

```
pockeat-api/
├── app/
│   ├── api/
│   │   ├── models/
│   │   │   ├── food_analysis.py
│   │   │   └── exercise_analysis.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── food_routes.py
│   │       └── exercise_routes.py
│   ├── services/
│   │   └── gemini/
│   │       ├── base_gemini_service.py
│   │       ├── exercise_analysis_service.py
│   │       ├── food_image_analysis_service.py
│   │       ├── food_text_analysis_service.py
│   │       └── nutrition_label_analysis_service.py
│   ├── __init__.py
│   └── config.py
├── tests/
├── .env
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

### Running Tests

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Google Gemini API for providing the AI capabilities
- The PockEat mobile app team for their collaboration
