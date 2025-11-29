from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime, date
import sqlite3
from typing import List
import database

app = FastAPI()

class Flight(BaseModel):
    id: int
    flight_no: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    price: float
    seats_available: int

def get_db():
    return sqlite3.connect('flights.db')

@app.on_event("startup")
def startup():
    database.add_sample_flights()

@app.get("/")
def home():
    return {"message": "Flight API"}

@app.get("/flights")
def get_flights(sort_by: str = "departure_time"):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM flights")
    rows = cursor.fetchall()
    conn.close()
    
    flights = []
    for row in rows:
        flights.append(Flight(
            id=row[0], flight_no=row[1], origin=row[2], destination=row[3],
            departure_time=row[4], arrival_time=row[5], price=row[6],
            seats_available=row[7]
        ))
    
    if sort_by == "price":
        flights.sort(key=lambda x: x.price)
    
    return flights

@app.get("/search")
def search_flights(origin: str, destination: str, date: str, sort_by: str = "departure_time"):
    if origin == destination:
        raise HTTPException(status_code=400, detail="Same origin and destination")
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM flights 
        WHERE origin = ? AND destination = ? 
        AND date(departure_time) = ?
    ''', (origin.upper(), destination.upper(), date))
    
    rows = cursor.fetchall()
    conn.close()
    
    flights = []
    for row in rows:
        flights.append(Flight(
            id=row[0], flight_no=row[1], origin=row[2], destination=row[3],
            departure_time=row[4], arrival_time=row[5], price=row[6],
            seats_available=row[7]
        ))
    
    if sort_by == "price":
        flights.sort(key=lambda x: x.price)
    
    return flights

@app.get("/flights/{flight_id}")
def get_flight(flight_id: int):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM flights WHERE id = ?", (flight_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    return Flight(
        id=row[0], flight_no=row[1], origin=row[2], destination=row[3],
        departure_time=row[4], arrival_time=row[5], price=row[6],
        seats_available=row[7]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)