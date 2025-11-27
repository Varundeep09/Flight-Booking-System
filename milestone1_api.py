from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
from milestone1_database import SessionLocal, Flight, create_tables, populate_sample_data
from datetime import timedelta

app = FastAPI(title="Flight Search API - Milestone 1")

# Pydantic models
class FlightResponse(BaseModel):
    id: int
    flight_no: str
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    seats_available: int
    duration_minutes: int

    class Config:
        from_attributes = True

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    create_tables()
    # Check if data exists, if not populate
    db = SessionLocal()
    if db.query(Flight).count() == 0:
        populate_sample_data()
    db.close()

@app.get("/flights", response_model=List[FlightResponse])
def get_all_flights(
    db: Session = Depends(get_db),
    sort_by: str = Query("departure_time", enum=["price", "departure_time", "duration"])
):
    """Retrieve all flights with optional sorting"""
    query = db.query(Flight)
    
    if sort_by == "price":
        query = query.order_by(Flight.price)
    elif sort_by == "duration":
        # Sort by duration (arrival - departure)
        flights = query.all()
        flights.sort(key=lambda f: (f.arrival_time - f.departure_time).total_seconds())
        return [_format_flight(f) for f in flights]
    else:
        query = query.order_by(Flight.departure_time)
    
    flights = query.all()
    return [_format_flight(f) for f in flights]

@app.get("/flights/search", response_model=List[FlightResponse])
def search_flights(
    origin: str = Query(..., min_length=3, max_length=3),
    destination: str = Query(..., min_length=3, max_length=3),
    date: date = Query(...),
    sort_by: str = Query("departure_time", enum=["price", "departure_time", "duration"]),
    db: Session = Depends(get_db)
):
    """Search flights by origin, destination and date"""
    
    # Input validation
    if origin == destination:
        raise HTTPException(status_code=400, detail="Origin and destination cannot be same")
    
    # Query flights
    query = db.query(Flight).filter(
        Flight.origin == origin.upper(),
        Flight.destination == destination.upper(),
        Flight.departure_time >= datetime.combine(date, datetime.min.time()),
        Flight.departure_time < datetime.combine(date, datetime.min.time()) + timedelta(days=1)
    )
    
    flights = query.all()
    
    # Sort results
    if sort_by == "price":
        flights.sort(key=lambda f: f.price)
    elif sort_by == "duration":
        flights.sort(key=lambda f: (f.arrival_time - f.departure_time).total_seconds())
    else:
        flights.sort(key=lambda f: f.departure_time)
    
    return [_format_flight(f) for f in flights]

@app.get("/flights/{flight_id}", response_model=FlightResponse)
def get_flight(flight_id: int, db: Session = Depends(get_db)):
    """Get specific flight by ID"""
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return _format_flight(flight)

def _format_flight(flight: Flight) -> FlightResponse:
    """Format flight object with calculated duration"""
    duration = (flight.arrival_time - flight.departure_time).total_seconds() / 60
    return FlightResponse(
        id=flight.id,
        flight_no=flight.flight_no,
        origin=flight.origin,
        destination=flight.destination,
        departure_time=flight.departure_time,
        arrival_time=flight.arrival_time,
        price=flight.price,
        seats_available=flight.seats_available,
        duration_minutes=int(duration)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)