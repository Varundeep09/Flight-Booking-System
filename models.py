from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random

engine = create_engine("sqlite:///flights.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Flight(Base):
    __tablename__ = "flights"
    
    id = Column(Integer, primary_key=True, index=True)
    flight_no = Column(String, unique=True, index=True)
    origin = Column(String, index=True)
    destination = Column(String, index=True)
    departure_time = Column(DateTime)
    arrival_time = Column(DateTime)
    price = Column(Float)
    seats_available = Column(Integer)

def create_tables():
    Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    airports = ["DEL", "BOM", "BLR", "MAA", "CCU", "HYD"]
    airlines = ["AI", "6E", "SG", "UK"]
    
    flights = []
    for i in range(50):
        origin, destination = random.sample(airports, 2)
        airline = random.choice(airlines)
        flight_no = f"{airline}{100 + i}"
        
        base_time = datetime.now() + timedelta(days=random.randint(0, 7))
        departure = base_time.replace(hour=random.randint(6, 22), minute=random.choice([0, 30]))
        arrival = departure + timedelta(hours=random.randint(1, 4))
        
        flight = Flight(
            flight_no=flight_no,
            origin=origin,
            destination=destination,
            departure_time=departure,
            arrival_time=arrival,
            price=random.randint(3000, 15000),
            seats_available=random.randint(10, 180)
        )
        flights.append(flight)
    
    db.add_all(flights)
    db.commit()
    db.close()

if __name__ == "__main__":
    create_tables()
    seed_data()
    print("Database initialized with sample data")