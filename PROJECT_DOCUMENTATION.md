# Flight Booking System Documentation

## Overview

A flight search and booking system with FastAPI and Django implementations.

## Features

- Flight search by origin, destination, date
- Price sorting and filtering
- Basic booking system
- SQLite database
- REST API endpoints

## Tech Stack

- **FastAPI**: Main API framework
- **Django**: Alternative implementation
- **SQLite**: Database
- **Python**: Backend language

## Project Structure

```
├── app.py              # FastAPI main app
├── database.py         # Database operations
├── models.py           # Alternative DB model
├── flight_booking/     # Django implementation
│   ├── flights/        # Flight app
│   └── bookings/       # Booking app
└── requirements.txt    # Dependencies
```

## API Usage

### Search Flights
```bash
curl "http://localhost:8000/search?origin=DEL&destination=BOM&date=2024-01-20"
```

### Get All Flights
```bash
curl "http://localhost:8000/flights"
```

## Database Schema

### Flights Table
- id, flight_no, origin, destination
- departure_time, arrival_time
- price, seats_available

### Bookings Table (Django)
- pnr, flight_id, passenger_name
- phone, seat_number, price, status

## Setup Instructions

1. Install dependencies: `pip install -r requirements.txt`
2. Run FastAPI: `python app.py`
3. Run Django: `cd flight_booking && python manage.py runserver`

## Testing

Use `test_api.py` to test endpoints or visit `/docs` for interactive testing.