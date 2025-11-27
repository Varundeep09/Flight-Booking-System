# Flight Booking System

A flight search and booking API built with FastAPI and SQLite.

## Features

- Search flights by origin, destination, and date
- Sort results by price, departure time, or duration
- SQLite database with sample flight data
- Input validation and error handling
- Interactive API documentation

## Setup

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

## API Endpoints

### Get All Flights
```
GET /flights?sort_by=price
```

### Search Flights
```
GET /search?origin=DEL&destination=BOM&date=2024-01-20&sort_by=price
```

### Get Flight by ID
```
GET /flights/1
```

## Testing

Visit http://localhost:8000/docs for interactive API documentation.

Example search:
```bash
curl "http://localhost:8000/search?origin=DEL&destination=BOM&date=2024-01-20"
```

## Database

The app uses SQLite with sample data including:
- 50 flights across 6 Indian airports
- 4 major airlines (AI, 6E, SG, UK)
- Flight schedules for the next 7 days

## Project Structure

```
├── app.py              # Main FastAPI application
├── database.py         # Database setup and sample data
├── requirements.txt    # Python dependencies
├── test_api.py         # API testing script
└── README.md          # This file
```