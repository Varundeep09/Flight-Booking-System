# Flight Booking System - Milestone 2

Flight search system with dynamic pricing engine that adjusts fares in real-time.

## Features

### Milestone 1
- Search flights by origin, destination, and date
- Get all flights with sorting options
- SQLite database with sample flight data
- Input validation and error handling

### Milestone 2 (New)
- Dynamic pricing based on multiple factors
- Real-time fare adjustment
- Price breakdown showing all factors
- Background simulator for demand changes
- Fare history tracking (optional)

## Dynamic Pricing Factors

1. **Seat Availability**: Price increases as seats fill up
   - >80% occupied: +50% price increase
   - >50% occupied: +20% price increase
   - <50% occupied: No increase

2. **Time Until Departure**: Price increases closer to departure
   - <24 hours: +40% increase
   - 1-3 days: +20% increase
   - 3-7 days: +10% increase
   - >7 days: No increase

3. **Demand Level**: Simulated market demand
   - High demand: +30% increase
   - Medium demand: +15% increase
   - Low demand: No increase

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. (Optional) Run demand simulator in separate terminal:
```bash
python simulator.py
```

4. Access API documentation:
```
http://localhost:8000/docs
```

## API Endpoints

### Get All Flights (with dynamic pricing)
```
GET /flights?sort_by=price
```

### Search Flights (with dynamic pricing)
```
GET /search?origin=DEL&destination=BOM&date=2024-01-20&sort_by=price
```

### Get Flight Price Details
```
GET /flights/{flight_id}/price
```

## Example Usage

```bash
# Get all flights with dynamic prices
curl "http://localhost:8000/flights"

# Search flights with dynamic pricing
curl "http://localhost:8000/search?origin=DEL&destination=BOM&date=2024-01-20"

# Get detailed price breakdown for a flight
curl "http://localhost:8000/flights/1/price"
```

## Example Response

```json
{
  "flight_no": "AI101",
  "origin": "DEL",
  "destination": "BOM",
  "departure_time": "2024-01-20T08:30:00",
  "base_fare": 5000,
  "dynamic_price": 7250,
  "price_factors": {
    "seat_factor": 0.2,
    "time_factor": 0.1,
    "demand_factor": 0.15,
    "demand_level": "medium"
  },
  "occupancy_percent": 65.5,
  "seats_available": 62
}
```

## Database

Uses SQLite database with:
- 30 flights across 6 Indian airports
- 4 airlines (AI, 6E, SG, UK)
- Flight schedules for next 7 days
- Fare history tracking table

## Project Structure

```
├── app.py              # Main FastAPI application
├── database.py         # Database setup and operations
├── pricing.py          # Dynamic pricing engine
├── simulator.py        # Background demand simulator
├── requirements.txt    # Dependencies
├── README.md          # This file
└── LICENSE            # MIT License
```

## How Dynamic Pricing Works

The pricing engine calculates the final fare using:

```
dynamic_price = base_fare × (1 + seat_factor + time_factor + demand_factor)
```

Each factor is calculated based on current conditions and adds a percentage to the base fare.




🔐 Sample Login Credentials
Username: admin
Password: admin123

Username: demo
Password: demo123

Username: test
Password: test123
