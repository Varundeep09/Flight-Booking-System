import sqlite3
from datetime import datetime, timedelta
import random

def create_database():
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY,
            flight_no TEXT UNIQUE,
            origin TEXT,
            destination TEXT,
            departure_time TEXT,
            arrival_time TEXT,
            price REAL,
            seats_available INTEGER,
            total_seats INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fare_history (
            id INTEGER PRIMARY KEY,
            flight_id INTEGER,
            price REAL,
            seats_available INTEGER,
            demand_level TEXT,
            recorded_at TEXT,
            FOREIGN KEY (flight_id) REFERENCES flights(id)
        )
    ''')
    
    conn.commit()
    return conn

def add_sample_data():
    conn = create_database()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM flights")
    conn.commit()
    
    airports = ["DEL", "BOM", "BLR", "MAA", "CCU", "HYD"]
    airlines = ["AI", "6E", "SG", "UK"]
    
    # Start from January 2026
    start_date = datetime(2026, 1, 1)
    
    for i in range(30):
        origin = random.choice(airports)
        destination = random.choice([a for a in airports if a != origin])
        airline = random.choice(airlines)
        
        days_ahead = random.randint(0, 30)
        hour = random.randint(6, 22)
        dep_time = start_date + timedelta(days=days_ahead)
        dep_time = dep_time.replace(hour=hour, minute=0, second=0, microsecond=0)
        arr_time = dep_time + timedelta(hours=random.randint(1, 4))
        
        total_seats = 180
        seats_available = random.randint(20, 150)
        
        cursor.execute('''
            INSERT INTO flights (flight_no, origin, destination, departure_time, 
                               arrival_time, price, seats_available, total_seats)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            f"{airline}{100 + i}",
            origin,
            destination,
            dep_time.isoformat(),
            arr_time.isoformat(),
            random.randint(3000, 12000),
            seats_available,
            total_seats
        ))
    
    conn.commit()
    conn.close()
    print("Sample flight data added for 2026")

def simulate_demand_change():
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, seats_available FROM flights")
    flights = cursor.fetchall()
    
    for flight_id, seats in flights:
        change = random.choice([-2, -1, 0, 0, 1])
        new_seats = max(0, min(180, seats + change))
        cursor.execute("UPDATE flights SET seats_available = ? WHERE id = ?", 
                      (new_seats, flight_id))
    
    conn.commit()
    conn.close()

def store_fare_history(flight_id, price, seats, demand_level):
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO fare_history (flight_id, price, seats_available, demand_level, recorded_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (flight_id, price, seats, demand_level, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def setup_flights():
    add_sample_data()

if __name__ == "__main__":
    setup_flights()