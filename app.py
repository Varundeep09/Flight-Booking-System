from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, date
import sqlite3
from typing import List
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

def get_db():
    return sqlite3.connect('flights.db')

@app.on_event("startup")
def startup():
    database.setup_flights()

@app.get("/")
def home():
    return {"message": "Flight Search API - Milestone 1"}

@app.get("/flights")
def get_all_flights(sort_by: str = "departure_time"):
    conn = get_db()
    cursor = conn.cursor()
    
    if sort_by == "price":
        cursor.execute("SELECT * FROM flights ORDER BY price")
    else:
        cursor.execute("SELECT * FROM flights ORDER BY departure_time")
    
    rows = cursor.fetchall()
    conn.close()
    
    flights = []
    for row in rows:
        flights.append(Flight(
            id=row[0], flight_no=row[1], origin=row[2], destination=row[3],
            departure_time=row[4], arrival_time=row[5], price=row[6], seats_available=row[7]
        ))
    
    return flights

@app.get("/search")
def search_flights(origin: str, destination: str, date: str, sort_by: str = "departure_time"):
    if origin == destination:
        raise HTTPException(status_code=400, detail="Origin and destination cannot be same")
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM flights WHERE origin = ? AND destination = ? AND date(departure_time) = ?"
    if sort_by == "price":
        query += " ORDER BY price"
    else:
        query += " ORDER BY departure_time"
    
    cursor.execute(query, (origin.upper(), destination.upper(), date))
    rows = cursor.fetchall()
    conn.close()
    
    flights = []
    for row in rows:
        flights.append(Flight(
            id=row[0], flight_no=row[1], origin=row[2], destination=row[3],
            departure_time=row[4], arrival_time=row[5], price=row[6], seats_available=row[7]
        ))
    
    return flights

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)