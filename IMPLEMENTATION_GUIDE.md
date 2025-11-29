# Flight Booking System - Setup Guide

## Quick Start

### 1. Setup
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run
```bash
python app.py
```

### 3. Test
Visit: http://localhost:8000/docs

## API Endpoints

- `GET /flights` - Get all flights
- `GET /search?origin=DEL&destination=BOM&date=2024-01-20` - Search flights
- `GET /flights/1` - Get flight by ID

## Database

Uses SQLite with sample flight data.

## Files

- `app.py` - Main API
- `database.py` - Database setup
- `models.py` - Alternative database model
- `test_api.py` - API testing

## Django Version

The `flight_booking/` folder contains a Django implementation with:
- Flight and booking models
- REST API endpoints
- Dynamic pricing
- Booking system