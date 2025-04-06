# PockEat API

[![Code Quality](https://github.com/Pemuda-Pembuka-Langkah/pockeat-api/actions/workflows/quality.yml/badge.svg)](https://github.com/Pemuda-Pembuka-Langkah/pockeat-api/actions/workflows/quality.yml)
[![codecov](https://codecov.io/gh/Pemuda-Pembuka-Langkah/pockeat-api/branch/main/graph/badge.svg)](https://codecov.io/gh/Pemuda-Pembuka-Langkah/pockeat-api)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Pemuda-Pembuka-Langkah_pockeat-api&metric=alert_status)](https://sonarcloud.io/dashboard?id=Pemuda-Pembuka-Langkah_pockeat-api)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Pemuda-Pembuka-Langkah_pockeat-api&metric=coverage)](https://sonarcloud.io/dashboard?id=Pemuda-Pembuka-Langkah_pockeat-api)

A FastAPI-based API for food and exercise analysis using Google's Gemini models.

## Features

- Food analysis from text descriptions
- Food analysis from images
- Nutrition label analysis from images
- Exercise analysis from text descriptions
- Corrections based on user feedback

## Requirements

- Python 3.10+
- Google API Key for Gemini models

## Setup

1. Clone the repository
```bash
git clone https://github.com/your-username/pockeat-api.git
cd pockeat-api
```

2. Create a virtual environment and install dependencies
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

3. Set up environment variables (create a `.env` file)
```
GOOGLE_API_KEY=your_api_key_here
HOST=0.0.0.0
PORT=8080
```

4. Run the application
```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Deployment on Railway

This project is ready to be deployed on Railway:

1. Create a new project on Railway
2. Connect your GitHub repository
3. Add the `GOOGLE_API_KEY` environment variable
4. Deploy the app

## Project Structure

```
pockeat-api/
├── api/                    # API package
│   ├── models/             # Pydantic models
│   │   ├── food_analysis.py     # Food analysis models
│   │   └── exercise_analysis.py # Exercise analysis models
│   └── services/           # Service implementations
│       ├── gemini/         # Gemini API services
│       │   ├── base_service.py    # Base service class
│       │   ├── food_service.py    # Food analysis service
│       │   ├── exercise_service.py # Exercise analysis service
│       │   ├── exceptions.py      # Custom exceptions
│       │   └── utils/             # Utility functions
│       └── gemini_service.py # Main service
├── main.py                # Main application file
├── Procfile               # Procfile for Railway deployment
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
``` 