from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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

@app.on_event("startup")
def startup():
    database.add_sample_flights()

@app.get("/flights")
def get_flights():
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights")
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
def search_flights(origin: str, destination: str, date: str):
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE origin = ? AND destination = ?", (origin, destination))
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
    uvicorn.run(app, port=8000)