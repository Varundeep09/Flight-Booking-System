# Milestone 1: Core Flight Search & Data Management

## ✅ Completed Tasks

### 1. Database Schema Design
- **SQLite database** with Flight table
- **Fields**: flight_no, origin, destination, departure_time, arrival_time, price, seats_available
- **Indexes** on origin, destination, flight_no for performance

### 2. Sample Data Population
- **50 flights** across 6 major Indian airports (DEL, BOM, BLR, MAA, CCU, HYD)
- **4 airlines**: AI (Air India), 6E (IndiGo), SG (SpiceJet), UK (Vistara)
- **7 days** of flight schedules with random timings and prices

### 3. REST API Implementation
- **FastAPI** framework for high-performance APIs
- **Automatic documentation** at `/docs`
- **Input validation** using Pydantic models

### 4. API Endpoints

#### Get All Flights
```
GET /flights?sort_by=price|departure_time|duration
```

#### Search Flights
```
GET /flights/search?origin=DEL&destination=BOM&date=2024-01-15&sort_by=price
```

#### Get Specific Flight
```
GET /flights/{flight_id}
```

### 5. Input Validation & Sorting
- **Airport codes**: 3-character validation
- **Date validation**: Proper date format required
- **Origin ≠ Destination**: Business rule validation
- **Sorting options**: Price, departure time, duration

## 🚀 Quick Start

### Option 1: Auto Setup
```bash
python milestone1_run.py
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r milestone1_requirements.txt

# Setup database
python milestone1_database.py

# Start API server
python milestone1_api.py
```

## 📡 API Testing

### Test Flight Search
```bash
curl "http://localhost:8000/flights/search?origin=DEL&destination=BOM&date=2024-01-15"
```

### Test All Flights
```bash
curl "http://localhost:8000/flights?sort_by=price"
```

### Interactive Documentation
Visit: http://localhost:8000/docs

## 📊 Sample Response
```json
[
  {
    "id": 1,
    "flight_no": "AI101",
    "origin": "DEL",
    "destination": "BOM",
    "departure_time": "2024-01-15T08:30:00",
    "arrival_time": "2024-01-15T11:00:00",
    "price": 5500.0,
    "seats_available": 120,
    "duration_minutes": 150
  }
]
```

## ✅ Milestone 1 Deliverables Achieved

- ✅ **Populated flight database** (SQLite with 50 sample flights)
- ✅ **Functional flight search API** with filtering by origin, destination, date
- ✅ **Input validation** (airport codes, date format, business rules)
- ✅ **Sorting functionality** (price, departure time, duration)
- ✅ **Simulated airline data** (4 airlines, 6 airports, 7 days schedule)

## 🔄 Next Steps (Milestone 2)
- Implement dynamic pricing engine
- Add seat availability factors
- Time-based price adjustments
- Demand simulation