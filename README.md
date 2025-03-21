# PockEat API

A RESTful API built with Flask for the PockEat application.

## Setup and Installation

1. Create a virtual environment:
   ```
   python -m venv env
   ```

2. Activate the virtual environment:
   - Windows:
     ```
     env\Scripts\activate
     ```
   - Mac/Linux:
     ```
     source env/bin/activate
     ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables by creating a `.env` file in the root directory.

5. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Run the development server:
   ```
   flask run
   ```

## API Endpoints

(Documentation will be added as endpoints are developed)

## Project Structure

```
pockeat-api/
├── app/
│   ├── __init__.py       # Flask application initialization
│   ├── config.py         # Configuration settings
│   ├── models/           # Database models
│   ├── routes/           # API routes and resources
│   ├── schemas/          # Marshmallow schemas for serialization
│   └── utils/            # Utility functions
├── migrations/           # Database migrations
├── tests/                # Test suite
├── .env                  # Environment variables (not in version control)
├── .gitignore            # Git ignore file
├── app.py                # Application entry point
└── requirements.txt      # Project dependencies
```
