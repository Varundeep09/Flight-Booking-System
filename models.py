import sqlite3
from datetime import datetime, timedelta
import random

def create_db():
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
    conn.close()

def add_flights():
    create_db()
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM flights")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    airports = ["DEL", "BOM", "BLR", "MAA"]
    
    for i in range(15):
        origin = random.choice(airports)
        dest = random.choice([a for a in airports if a != origin])
        
        dep_time = datetime.now() + timedelta(days=random.randint(0, 3))
        arr_time = dep_time + timedelta(hours=2)
        
        cursor.execute('''
            INSERT INTO flights VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            i+1, f"AI{100+i}", origin, dest,
            dep_time.isoformat(), arr_time.isoformat(),
            random.randint(5000, 10000), random.randint(50, 100)
        ))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_flights()