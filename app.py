from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime, date
import sqlite3
from typing import List, Optional
import database

app = FastAPI(title="Flight Search API")

class Flight(BaseModel):
    id: int
    flight_no: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    price: float
    seats_available: int
    duration_hours: float

def get_db_connection():
    return sqlite3.connect('flights.db')

def calculate_duration(dep_time_str, arr_time_str):
    dep = datetime.fromisoformat(dep_time_str)
    arr = datetime.fromisoformat(arr_time_str)
    return round((arr - dep).total_seconds() / 3600, 2)

@app.on_event("startup")
def startup():
    database.add_sample_flights()

@app.get("/")
def home():
    return {"message": "Flight Search API is running", "docs": "/docs"}

@app.get("/flights", response_model=List[Flight])
def get_flights(sort_by: str = Query("departure_time", pattern="^(price|departure_time|duration)$")):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM flights")
    rows = cursor.fetchall()
    conn.close()
    
    flights = []
    for row in rows:
        duration = calculate_duration(row[4], row[5])
        flights.append(Flight(
            id=row[0], flight_no=row[1], origin=row[2], destination=row[3],
            departure_time=row[4], arrival_time=row[5], price=row[6],
            seats_available=row[7], duration_hours=duration
        ))
    
    # Sort flights
    if sort_by == "price":
        flights.sort(key=lambda x: x.price)
    elif sort_by == "duration":
        flights.sort(key=lambda x: x.duration_hours)
    else:
        flights.sort(key=lambda x: x.departure_time)
    
    return flights

@app.get("/search", response_model=List[Flight])
def search_flights(
    origin: str = Query(..., min_length=3, max_length=3),
    destination: str = Query(..., min_length=3, max_length=3),
    travel_date: date = Query(..., alias="date"),
    sort_by: str = Query("departure_time", pattern="^(price|departure_time|duration)$")
):
    if origin.upper() == destination.upper():
        raise HTTPException(status_code=400, detail="Origin and destination must be different")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Search for flights on specific date
    date_start = travel_date.strftime("%Y-%m-%d")
    date_end = (travel_date.strftime("%Y-%m-%d"))
    
    cursor.execute('''
        SELECT * FROM flights 
        WHERE origin = ? AND destination = ? 
        AND date(departure_time) = ?
    ''', (origin.upper(), destination.upper(), date_start))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return []
    
    flights = []
    for row in rows:
        duration = calculate_duration(row[4], row[5])
        flights.append(Flight(
            id=row[0], flight_no=row[1], origin=row[2], destination=row[3],
            departure_time=row[4], arrival_time=row[5], price=row[6],
            seats_available=row[7], duration_hours=duration
        ))
    
    # Apply sorting
    if sort_by == "price":
        flights.sort(key=lambda x: x.price)
    elif sort_by == "duration":
        flights.sort(key=lambda x: x.duration_hours)
    else:
        flights.sort(key=lambda x: x.departure_time)
    
    return flights

@app.get("/flights/{flight_id}", response_model=Flight)
def get_flight_by_id(flight_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM flights WHERE id = ?", (flight_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    duration = calculate_duration(row[4], row[5])
    return Flight(
        id=row[0], flight_no=row[1], origin=row[2], destination=row[3],
        departure_time=row[4], arrival_time=row[5], price=row[6],
        seats_available=row[7], duration_hours=duration
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)