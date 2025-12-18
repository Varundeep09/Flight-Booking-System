import sqlite3
from datetime import datetime, timedelta
import random
import string
import hashlib

def create_database():
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT,
            full_name TEXT,
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY,
            city_name TEXT,
            airport_code TEXT,
            country TEXT DEFAULT 'India'
        )
    ''')
    
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
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            pnr TEXT UNIQUE,
            user_id INTEGER,
            flight_id INTEGER,
            passenger_name TEXT,
            passenger_age INTEGER,
            passenger_phone TEXT,
            passenger_email TEXT,
            seat_number TEXT,
            booking_status TEXT DEFAULT 'CONFIRMED',
            final_price REAL,
            booking_time TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (flight_id) REFERENCES flights(id)
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

def add_cities_data():
    conn = create_database()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM cities")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    cities_data = [
        ("Delhi", "DEL"), ("Mumbai", "BOM"), ("Bangalore", "BLR"),
        ("Chennai", "MAA"), ("Kolkata", "CCU"), ("Hyderabad", "HYD"),
        ("Ahmedabad", "AMD"), ("Goa", "GOI"), ("Pune", "PNQ"),
        ("Jaipur", "JAI"), ("Kochi", "COK"), ("Thiruvananthapuram", "TRV"),
        ("Lucknow", "LKO"), ("Bhubaneswar", "BBI"), ("Indore", "IDR"),
        ("Nagpur", "NAG"), ("Coimbatore", "CJB"), ("Vadodara", "BDQ"),
        ("Visakhapatnam", "VTZ"), ("Patna", "PAT")
    ]
    
    for city, code in cities_data:
        cursor.execute("INSERT INTO cities (city_name, airport_code) VALUES (?, ?)", (city, code))
    
    conn.commit()
    conn.close()

def add_sample_data():
    conn = create_database()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM flights")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    airports = ["DEL", "BOM", "BLR", "MAA", "CCU", "HYD"]
    airlines = ["AI", "6E", "SG", "UK"]
    
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

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password, full_name):
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password_hash, full_name, datetime.now().isoformat()))
        
        conn.commit()
        return True, "User created successfully"
    except sqlite3.IntegrityError:
        return False, "Username or email already exists"
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    cursor.execute("SELECT id, username, full_name FROM users WHERE username = ? AND password_hash = ?", 
                  (username, password_hash))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return True, {"id": result[0], "username": result[1], "full_name": result[2]}
    return False, None

def search_cities(query):
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT city_name, airport_code FROM cities 
        WHERE city_name LIKE ? OR airport_code LIKE ?
        ORDER BY city_name
        LIMIT 10
    ''', (f"%{query}%", f"%{query}%"))
    
    results = cursor.fetchall()
    conn.close()
    
    return [{"city": row[0], "code": row[1]} for row in results]

def generate_pnr():
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=4))
    return letters + numbers

def book_flight(flight_id, user_id, passenger_data, seat_number, final_price):
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        cursor.execute("SELECT seats_available FROM flights WHERE id = ?", (flight_id,))
        result = cursor.fetchone()
        
        if not result or result[0] <= 0:
            cursor.execute("ROLLBACK")
            return None, "No seats available"
        
        pnr = generate_pnr()
        while True:
            cursor.execute("SELECT id FROM bookings WHERE pnr = ?", (pnr,))
            if not cursor.fetchone():
                break
            pnr = generate_pnr()
        
        payment_success = random.random() < 0.9
        if not payment_success:
            cursor.execute("ROLLBACK")
            return None, "Payment failed"
        
        cursor.execute('''
            INSERT INTO bookings (pnr, user_id, flight_id, passenger_name, passenger_age, 
                                passenger_phone, passenger_email, seat_number, 
                                final_price, booking_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pnr, user_id, flight_id, passenger_data['name'], passenger_data['age'],
            passenger_data['phone'], passenger_data.get('email', ''),
            seat_number, final_price, datetime.now().isoformat()
        ))
        
        cursor.execute("UPDATE flights SET seats_available = seats_available - 1 WHERE id = ?", (flight_id,))
        
        cursor.execute("COMMIT")
        return pnr, "Booking successful"
        
    except Exception as e:
        cursor.execute("ROLLBACK")
        return None, f"Booking failed: {str(e)}"
    finally:
        conn.close()

def cancel_booking(pnr):
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        cursor.execute("SELECT flight_id FROM bookings WHERE pnr = ? AND booking_status = 'CONFIRMED'", (pnr,))
        result = cursor.fetchone()
        
        if not result:
            cursor.execute("ROLLBACK")
            return False, "Booking not found or already cancelled"
        
        flight_id = result[0]
        
        cursor.execute("UPDATE bookings SET booking_status = 'CANCELLED' WHERE pnr = ?", (pnr,))
        cursor.execute("UPDATE flights SET seats_available = seats_available + 1 WHERE id = ?", (flight_id,))
        
        cursor.execute("COMMIT")
        return True, "Booking cancelled successfully"
        
    except Exception as e:
        cursor.execute("ROLLBACK")
        return False, f"Cancellation failed: {str(e)}"
    finally:
        conn.close()

def get_booking_details(pnr):
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT b.*, f.flight_no, f.origin, f.destination, f.departure_time, f.arrival_time
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        WHERE b.pnr = ?
    ''', (pnr,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'pnr': result[1],
            'flight_no': result[12],
            'origin': result[13],
            'destination': result[14],
            'departure_time': result[15],
            'arrival_time': result[16],
            'passenger_name': result[4],
            'passenger_age': result[5],
            'passenger_phone': result[6],
            'passenger_email': result[7],
            'seat_number': result[8],
            'booking_status': result[9],
            'final_price': result[10],
            'booking_time': result[11]
        }
    return None

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

def setup_flights():
    add_cities_data()
    add_sample_data()

if __name__ == "__main__":
    setup_flights()