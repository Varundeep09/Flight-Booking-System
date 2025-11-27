import sqlite3
from datetime import datetime, timedelta
import random

def init_db():
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    
    # Create flights table
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

def add_sample_flights():
    conn = init_db()
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM flights")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    airports = ["DEL", "BOM", "BLR", "MAA", "CCU", "HYD"]
    airlines = ["AI", "6E", "SG", "UK"]
    
    flight_data = []
    for i in range(1, 51):
        origin = random.choice(airports)
        destination = random.choice([a for a in airports if a != origin])
        airline = random.choice(airlines)
        
        # Generate times for next week
        days_ahead = random.randint(0, 7)
        base_date = datetime.now() + timedelta(days=days_ahead)
        
        dep_hour = random.randint(6, 22)
        dep_time = base_date.replace(hour=dep_hour, minute=random.choice([0, 30]))
        arr_time = dep_time + timedelta(hours=random.randint(1, 4))
        
        flight_data.append((
            f"{airline}{100 + i}",
            origin,
            destination,
            dep_time.isoformat(),
            arr_time.isoformat(),
            random.randint(3000, 15000),
            random.randint(20, 180)
        ))
    
    cursor.executemany('''
        INSERT INTO flights (flight_no, origin, destination, departure_time, 
                           arrival_time, price, seats_available)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', flight_data)
    
    conn.commit()
    conn.close()
    print(f"Added {len(flight_data)} sample flights to database")

if __name__ == "__main__":
    add_sample_flights()