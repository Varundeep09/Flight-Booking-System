from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import sqlite3
from typing import List
import database
import pricing

app = FastAPI(title="Flight Booking System")

@app.get("/", response_class=HTMLResponse)
def home():
    try:
        with open("templates/index.html", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>Error loading page</h1>"

class Flight(BaseModel):
    id: int
    flight_no: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    price: float
    seats_available: int

class FlightWithPrice(BaseModel):
    id: int
    flight_no: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    base_fare: float
    dynamic_price: float
    seats_available: int
    total_seats: int
    price_breakdown: dict

def get_db():
    return sqlite3.connect('flights.db')

@app.on_event("startup")
async def startup():
    database.setup_flights()



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
        dynamic_price = pricing.calculate_dynamic_price(
            row[6], row[7], row[8], row[4]
        )
        flights.append({
            "id": row[0],
            "flight_no": row[1],
            "origin": row[2],
            "destination": row[3],
            "departure_time": row[4],
            "arrival_time": row[5],
            "base_fare": row[6],
            "dynamic_price": dynamic_price,
            "seats_available": row[7]
        })
    
    return flights

@app.get("/search")
def search_flights(origin: str, destination: str, date: str, sort_by: str = "departure_time"):
    if origin == destination:
        raise HTTPException(status_code=400, detail="Origin and destination cannot be same")
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM flights WHERE origin = ? AND destination = ? AND date(departure_time) = ?"
    cursor.execute(query, (origin.upper(), destination.upper(), date))
    rows = cursor.fetchall()
    conn.close()
    
    flights = []
    for row in rows:
        dynamic_price = pricing.calculate_dynamic_price(
            row[6], row[7], row[8], row[4]
        )
        flights.append({
            "id": row[0],
            "flight_no": row[1],
            "origin": row[2],
            "destination": row[3],
            "departure_time": row[4],
            "arrival_time": row[5],
            "base_fare": row[6],
            "dynamic_price": dynamic_price,
            "seats_available": row[7]
        })
    
    if sort_by == "price":
        flights.sort(key=lambda x: x['dynamic_price'])
    
    return flights

@app.get("/flights/{flight_id}/price")
def get_flight_price(flight_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE id = ?", (flight_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    price_info = pricing.get_price_breakdown(
        row[6], row[7], row[8], row[4]
    )
    
    return {
        "flight_no": row[1],
        "origin": row[2],
        "destination": row[3],
        "departure_time": row[4],
        "base_fare": price_info['base_fare'],
        "dynamic_price": price_info['dynamic_price'],
        "price_factors": {
            "seat_factor": price_info['seat_factor'],
            "time_factor": price_info['time_factor'],
            "demand_factor": price_info['demand_factor'],
            "demand_level": price_info['demand_level']
        },
        "occupancy_percent": price_info['occupancy'],
        "seats_available": row[7]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)