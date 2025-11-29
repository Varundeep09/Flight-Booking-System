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
            seats_available INTEGER
        )
    ''')
    
    conn.commit()
    return conn

def add_sample_data():
    conn = create_database()
    cursor = conn.cursor()
    
    # Check if data exists
    cursor.execute("SELECT COUNT(*) FROM flights")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Sample airports and airlines
    airports = ["DEL", "BOM", "BLR", "MAA", "CCU", "HYD"]
    airlines = ["AI", "6E", "SG", "UK"]
    
    # Generate 30 sample flights
    for i in range(30):
        origin = random.choice(airports)
        destination = random.choice([a for a in airports if a != origin])
        airline = random.choice(airlines)
        
        # Generate flight times
        days_ahead = random.randint(0, 7)
        hour = random.randint(6, 22)
        dep_time = datetime.now() + timedelta(days=days_ahead)
        dep_time = dep_time.replace(hour=hour, minute=0, second=0, microsecond=0)
        arr_time = dep_time + timedelta(hours=random.randint(1, 4))
        
        cursor.execute('''
            INSERT INTO flights (flight_no, origin, destination, departure_time, 
                               arrival_time, price, seats_available)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            f"{airline}{100 + i}",
            origin,
            destination,
            dep_time.isoformat(),
            arr_time.isoformat(),
            random.randint(3000, 12000),
            random.randint(20, 150)
        ))
    
    conn.commit()
    conn.close()
    print("Sample flight data added to database")

def setup_flights():
    add_sample_data()

if __name__ == "__main__":
    setup_flights()