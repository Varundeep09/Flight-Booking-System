# Flight Booking System

Simple flight search API built with FastAPI.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

## Usage

- Get all flights: `GET /flights`
- Search flights: `GET /search?origin=DEL&destination=BOM&date=2024-01-20`
- Get flight by ID: `GET /flights/1`

## API Docs

Visit http://localhost:8000/docs

## Test

```bash
curl "http://localhost:8000/search?origin=DEL&destination=BOM&date=2024-01-20"
```