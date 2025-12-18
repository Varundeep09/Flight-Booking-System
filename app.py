from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import sqlite3
from typing import List, Optional
import database
import pricing

app = FastAPI(title="Flight Booking System")

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    username: str
    password: str

class BookingRequest(BaseModel):
    flight_id: int
    passenger_name: str
    passenger_age: int
    passenger_phone: str
    passenger_email: Optional[str] = ""
    seat_number: str

@app.get("/", response_class=HTMLResponse)
def home():
    return '<script>window.location.href="/login"</script>'

@app.get("/login", response_class=HTMLResponse)
def login_page():
    try:
        with open("templates/login.html", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>Login page not found</h1>"

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    try:
        with open("templates/dashboard.html", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>Dashboard not found</h1>"

@app.get("/book/{flight_id}", response_class=HTMLResponse)
def booking_page(flight_id: int):
    try:
        with open("templates/booking.html", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>Booking page not found</h1>"

@app.get("/manage", response_class=HTMLResponse)
def manage_booking():
    try:
        with open("templates/booking_status.html", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>Booking management page not found</h1>"

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
async def startup():
    database.setup_flights()

@app.post("/auth/signup")
def signup(user: UserCreate):
    success, message = database.create_user(
        user.username, user.email, user.password, user.full_name
    )
    
    if success:
        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)

@app.post("/auth/login")
def login(user: UserLogin):
    success, user_data = database.verify_user(user.username, user.password)
    
    if success:
        return {"success": True, "user": user_data}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

@app.get("/cities/search")
def search_cities(q: str):
    return database.search_cities(q)

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

@app.get("/flights/{flight_id}")
def get_flight_details(flight_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE id = ?", (flight_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    dynamic_price = pricing.calculate_dynamic_price(
        row[6], row[7], row[8], row[4]
    )
    
    return {
        "id": row[0],
        "flight_no": row[1],
        "origin": row[2],
        "destination": row[3],
        "departure_time": row[4],
        "arrival_time": row[5],
        "base_fare": row[6],
        "dynamic_price": dynamic_price,
        "seats_available": row[7],
        "total_seats": row[8]
    }

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

@app.post("/bookings/create")
def create_booking(booking: BookingRequest):
    # Get flight details and calculate final price
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE id = ?", (booking.flight_id,))
    flight_row = cursor.fetchone()
    conn.close()
    
    if not flight_row:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    final_price = pricing.calculate_dynamic_price(
        flight_row[6], flight_row[7], flight_row[8], flight_row[4]
    )
    
    passenger_data = {
        'name': booking.passenger_name,
        'age': booking.passenger_age,
        'phone': booking.passenger_phone,
        'email': booking.passenger_email
    }
    
    pnr, message = database.book_flight(
        booking.flight_id, 1, passenger_data, booking.seat_number, final_price
    )
    
    if pnr:
        return {
            "success": True,
            "pnr": pnr,
            "message": message,
            "final_price": final_price
        }
    else:
        raise HTTPException(status_code=400, detail=message)

@app.get("/bookings/{pnr}")
def get_booking(pnr: str):
    booking_details = database.get_booking_details(pnr.upper())
    
    if not booking_details:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return booking_details

@app.delete("/bookings/{pnr}/cancel")
def cancel_booking(pnr: str):
    success, message = database.cancel_booking(pnr.upper())
    
    if success:
        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)

@app.get("/seats/{flight_id}")
def get_available_seats(flight_id: int):
    conn = get_db()
    cursor = conn.cursor()
    
    # Get booked seats
    cursor.execute("SELECT seat_number FROM bookings WHERE flight_id = ? AND booking_status = 'CONFIRMED'", (flight_id,))
    booked_seats = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    # Generate seat map (simplified)
    all_seats = []
    for row in range(1, 31):  # 30 rows
        for seat in ['A', 'B', 'C', 'D', 'E', 'F']:
            seat_number = f"{row}{seat}"
            all_seats.append({
                'seat_number': seat_number,
                'available': seat_number not in booked_seats,
                'type': 'business' if row <= 5 else 'economy'
            })
    
    return all_seats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)