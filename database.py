import sqlite3
from datetime import datetime, timedelta
import random

def setup_db():
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY,
            flight_no TEXT,
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

def add_sample_flights():
    conn = setup_db()
    cursor = conn.cursor()
    
    # Check if we already have data
    cursor.execute("SELECT COUNT(*) FROM flights")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Add some flights
    airports = ["DEL", "BOM", "BLR", "MAA"]
    airlines = ["AI", "6E", "SG"]
    
    for i in range(20):
        origin = random.choice(airports)
        dest = random.choice([a for a in airports if a != origin])
        airline = random.choice(airlines)
        
        # Make departure time
        days = random.randint(0, 5)
        hour = random.randint(6, 20)
        dep_time = datetime.now() + timedelta(days=days)
        dep_time = dep_time.replace(hour=hour, minute=0)
        arr_time = dep_time + timedelta(hours=random.randint(1, 3))
        
        cursor.execute('''
            INSERT INTO flights (flight_no, origin, destination, departure_time, 
                               arrival_time, price, seats_available)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            f"{airline}{100+i}",
            origin,
            dest,
            dep_time.isoformat(),
            arr_time.isoformat(),
            random.randint(4000, 12000),
            random.randint(50, 150)
        ))
    
    conn.commit()
    conn.close()
    print("Added sample flights")

if __name__ == "__main__":
    add_sample_flights()