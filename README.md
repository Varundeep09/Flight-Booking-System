# Flight Search API - Milestone 1

Flight search system with REST API endpoints for searching and retrieving flight data.

## Features

- Search flights by origin, destination, and date
- Get all flights with sorting options
- SQLite database with sample flight data
- Input validation and error handling

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access API documentation:
```
http://localhost:8000/docs
```

## API Endpoints

### Get All Flights
```
GET /flights?sort_by=price
GET /flights?sort_by=departure_time
```

### Search Flights
```
GET /search?origin=DEL&destination=BOM&date=2024-01-20
GET /search?origin=DEL&destination=BOM&date=2024-01-20&sort_by=price
```

## Example Usage

```bash
# Get all flights sorted by price
curl "http://localhost:8000/flights?sort_by=price"

# Search flights from Delhi to Mumbai
curl "http://localhost:8000/search?origin=DEL&destination=BOM&date=2024-01-20"
```

## Database

Uses SQLite database with sample data including:
- 30 flights across 6 Indian airports
- 4 airlines (AI, 6E, SG, UK)
- Random flight schedules for next 7 days

## Project Structure

```
├── app.py              # Main FastAPI application
├── database.py         # Database setup and sample data
├── requirements.txt    # Dependencies
├── README.md          # This file
└── LICENSE            # MIT License
```