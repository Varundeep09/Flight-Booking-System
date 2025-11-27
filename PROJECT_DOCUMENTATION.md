# Flight Booking Simulator with Dynamic Pricing - Complete Project Documentation

## PART 1 — PROJECT OVERVIEW

### System Description
The Flight Booking Simulator with Dynamic Pricing is a full-stack web application that replicates real airline reservation systems like MakeMyTrip, IndiGo, and Air India. The system provides comprehensive flight booking functionality with intelligent pricing algorithms.

### Core Features
- **Flight Search**: Multi-criteria search with origin, destination, date, and filters
- **Dynamic Pricing**: Real-time fare calculation based on demand, availability, and time
- **Booking Workflow**: Complete reservation process with seat selection and payment
- **Concurrency Control**: Thread-safe booking system preventing double bookings
- **PNR Generation**: Unique booking reference with receipt download
- **Admin Dashboard**: Flight management and booking analytics

### Technology Stack
- **Backend**: Python + Django + Django REST Framework
- **Database**: MySQL (SQLite for development)
- **Frontend**: HTML5 + CSS3 (Bootstrap/Tailwind) + JavaScript
- **Architecture**: MVC pattern with service layer separation

## PART 2 — SYSTEM ARCHITECTURE

### 1. Three-Tier Architecture

#### Presentation Layer (Frontend)
- **Technologies**: HTML5, CSS3, JavaScript, Bootstrap/Tailwind
- **Components**: Search forms, flight results, booking flow, PNR confirmation
- **Responsibilities**: User interaction, data display, form validation

#### Business Logic Layer (Backend)
- **Framework**: Django with Django REST Framework
- **Services**: Pricing engine, booking service, payment simulation
- **APIs**: RESTful endpoints for all operations
- **Security**: Authentication, input validation, CSRF protection

#### Data Layer (Database)
- **Primary**: MySQL for production
- **Development**: SQLite for local development
- **Features**: ACID transactions, foreign key constraints, indexing

### 2. Component Interaction Flow
```
User Request → Frontend → Django Views → Services → Models → Database
                    ↓
Response ← JSON API ← Serializers ← Business Logic ← Query Results
```

## PART 3 — DATABASE SCHEMA DESIGN

### Core Tables Structure

#### Airlines Table
```sql
CREATE TABLE airlines (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(3) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Airports Table
```sql
CREATE TABLE airports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    iata_code VARCHAR(3) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Flights Table
```sql
CREATE TABLE flights (
    id INT PRIMARY KEY AUTO_INCREMENT,
    flight_no VARCHAR(10) UNIQUE NOT NULL,
    airline_id INT NOT NULL,
    origin_id INT NOT NULL,
    destination_id INT NOT NULL,
    departure_time DATETIME NOT NULL,
    arrival_time DATETIME NOT NULL,
    base_fare DECIMAL(10,2) NOT NULL,
    total_seats INT NOT NULL DEFAULT 180,
    seats_available INT NOT NULL,
    aircraft_type VARCHAR(50),
    status ENUM('SCHEDULED', 'DELAYED', 'CANCELLED') DEFAULT 'SCHEDULED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (airline_id) REFERENCES airlines(id),
    FOREIGN KEY (origin_id) REFERENCES airports(id),
    FOREIGN KEY (destination_id) REFERENCES airports(id),
    CHECK (seats_available >= 0),
    CHECK (seats_available <= total_seats),
    CHECK (departure_time < arrival_time)
);
```

#### Bookings Table
```sql
CREATE TABLE bookings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    pnr VARCHAR(10) UNIQUE NOT NULL,
    flight_id INT NOT NULL,
    passenger_name VARCHAR(200) NOT NULL,
    passenger_age INT NOT NULL,
    passenger_phone VARCHAR(15) NOT NULL,
    passenger_email VARCHAR(100),
    seat_number VARCHAR(5) NOT NULL,
    booking_status ENUM('CONFIRMED', 'CANCELLED', 'PENDING') DEFAULT 'PENDING',
    final_fare DECIMAL(10,2) NOT NULL,
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_status ENUM('SUCCESS', 'FAILED', 'PENDING') DEFAULT 'PENDING',
    FOREIGN KEY (flight_id) REFERENCES flights(id),
    CHECK (passenger_age > 0 AND passenger_age < 120)
);
```

#### Fare History Table (Analytics)
```sql
CREATE TABLE fare_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    flight_id INT NOT NULL,
    calculated_fare DECIMAL(10,2) NOT NULL,
    seats_remaining INT NOT NULL,
    demand_level ENUM('LOW', 'MEDIUM', 'HIGH') NOT NULL,
    time_to_departure INT NOT NULL, -- hours
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (flight_id) REFERENCES flights(id)
);
```

### Database Relationships
- **Airlines** → **Flights** (One-to-Many)
- **Airports** → **Flights** (One-to-Many for origin and destination)
- **Flights** → **Bookings** (One-to-Many)
- **Flights** → **Fare History** (One-to-Many)

### Key SQL Operations Used

#### Complex Joins
```sql
-- Flight search with airline and airport details
SELECT 
    f.flight_no,
    a.name as airline_name,
    orig.iata_code as origin_code,
    dest.iata_code as destination_code,
    f.departure_time,
    f.arrival_time,
    f.base_fare,
    f.seats_available
FROM flights f
JOIN airlines a ON f.airline_id = a.id
JOIN airports orig ON f.origin_id = orig.id
JOIN airports dest ON f.destination_id = dest.id
WHERE orig.iata_code = 'DEL' 
AND dest.iata_code = 'BOM'
AND DATE(f.departure_time) = '2024-01-15';
```

#### Transactions for Booking
```sql
START TRANSACTION;

-- Lock the flight row for update
SELECT seats_available FROM flights 
WHERE id = 1 FOR UPDATE;

-- Check availability and update
UPDATE flights 
SET seats_available = seats_available - 1 
WHERE id = 1 AND seats_available > 0;

-- Insert booking record
INSERT INTO bookings (pnr, flight_id, passenger_name, ...) 
VALUES ('AI729152', 1, 'John Doe', ...);

COMMIT;
```

## PART 4 — DYNAMIC PRICING ENGINE

### Pricing Algorithm Components

#### 1. Seat Availability Factor
```python
def calculate_seat_factor(seats_available, total_seats):
    occupancy_rate = (total_seats - seats_available) / total_seats
    
    if occupancy_rate >= 0.8:  # Less than 20% seats left
        return 1.5  # 50% increase
    elif occupancy_rate >= 0.5:  # 50-80% occupied
        return 1.2  # 20% increase
    elif occupancy_rate >= 0.3:  # 30-50% occupied
        return 1.1  # 10% increase
    else:
        return 0.95  # 5% discount for low occupancy
```

#### 2. Time-to-Departure Factor
```python
def calculate_time_factor(departure_time):
    from datetime import datetime, timedelta
    
    now = datetime.now()
    time_diff = departure_time - now
    hours_left = time_diff.total_seconds() / 3600
    
    if hours_left < 24:
        return 1.4  # 40% increase
    elif hours_left < 72:  # 1-3 days
        return 1.2  # 20% increase
    elif hours_left < 168:  # 3-7 days
        return 1.1  # 10% increase
    else:
        return 1.0  # No change
```

#### 3. Demand Simulation Factor
```python
def calculate_demand_factor(flight_id):
    # Simulate demand based on route popularity and random factors
    import random
    
    # Base demand levels
    demand_levels = {
        'LOW': 1.0,
        'MEDIUM': 1.15,
        'HIGH': 1.3
    }
    
    # Simulate current demand (could be based on search volume, bookings, etc.)
    current_demand = random.choice(['LOW', 'MEDIUM', 'HIGH'])
    return demand_levels[current_demand]
```

#### 4. Final Price Calculation
```python
def calculate_dynamic_fare(flight):
    base_fare = flight.base_fare
    
    seat_factor = calculate_seat_factor(
        flight.seats_available, 
        flight.total_seats
    )
    
    time_factor = calculate_time_factor(flight.departure_time)
    demand_factor = calculate_demand_factor(flight.id)
    
    # Apply all factors
    dynamic_fare = base_fare * seat_factor * time_factor * demand_factor
    
    # Round to nearest rupee
    return round(dynamic_fare, 2)
```

### Pricing Tiers Example
```
Base Fare: ₹5,000

Scenario 1 (Peak Demand):
- Seats Available: 10/180 (94% occupied) → Factor: 1.5
- Time Left: 12 hours → Factor: 1.4  
- Demand: HIGH → Factor: 1.3
- Final Price: ₹5,000 × 1.5 × 1.4 × 1.3 = ₹13,650

Scenario 2 (Low Demand):
- Seats Available: 120/180 (33% occupied) → Factor: 0.95
- Time Left: 10 days → Factor: 1.0
- Demand: LOW → Factor: 1.0  
- Final Price: ₹5,000 × 0.95 × 1.0 × 1.0 = ₹4,750
```

## PART 5 — MILESTONE-WISE IMPLEMENTATION

### MILESTONE 1: Core Flight Search & Data Management (Weeks 1-2)

#### Objectives
- Set up Django project structure
- Design and implement database schema
- Create flight search APIs
- Populate database with sample data

#### Implementation Steps

1. **Django Project Setup**
```bash
django-admin startproject flight_booking
cd flight_booking
python manage.py startapp flights
python manage.py startapp bookings
```

2. **Database Models** (flights/models.py)
```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Airline(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Airport(models.Model):
    iata_code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class Flight(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('DELAYED', 'Delayed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    flight_no = models.CharField(max_length=10, unique=True)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departing_flights')
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arriving_flights')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    total_seats = models.IntegerField(default=180)
    seats_available = models.IntegerField()
    aircraft_type = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='SCHEDULED')
    created_at = models.DateTimeField(auto_now_add=True)
```

3. **Flight Search API** (flights/views.py)
```python
from rest_framework import generics, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Flight
from .serializers import FlightSerializer

class FlightSearchView(generics.ListAPIView):
    queryset = Flight.objects.select_related('airline', 'origin', 'destination')
    serializer_class = FlightSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['origin__iata_code', 'destination__iata_code']
    ordering_fields = ['base_fare', 'departure_time', 'arrival_time']
    ordering = ['departure_time']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(departure_time__date=date)
        return queryset.filter(status='SCHEDULED', seats_available__gt=0)
```

#### Deliverables
- Functional Django project with proper structure
- Database schema with sample data
- Flight search API with filtering and sorting
- Basic admin interface for data management

### MILESTONE 2: Dynamic Pricing Engine (Weeks 3-4)

#### Objectives
- Implement dynamic pricing algorithm
- Integrate pricing engine with search API
- Create fare history tracking
- Add demand simulation

#### Implementation Steps

1. **Pricing Service** (flights/services/pricing.py)
```python
from datetime import datetime
import random
from decimal import Decimal

class PricingEngine:
    @staticmethod
    def calculate_seat_factor(seats_available, total_seats):
        occupancy_rate = (total_seats - seats_available) / total_seats
        
        if occupancy_rate >= 0.8:
            return Decimal('1.5')
        elif occupancy_rate >= 0.5:
            return Decimal('1.2')
        elif occupancy_rate >= 0.3:
            return Decimal('1.1')
        else:
            return Decimal('0.95')
    
    @staticmethod
    def calculate_time_factor(departure_time):
        now = datetime.now()
        if departure_time.tzinfo is None:
            departure_time = departure_time.replace(tzinfo=now.tzinfo)
        
        time_diff = departure_time - now
        hours_left = time_diff.total_seconds() / 3600
        
        if hours_left < 24:
            return Decimal('1.4')
        elif hours_left < 72:
            return Decimal('1.2')
        elif hours_left < 168:
            return Decimal('1.1')
        else:
            return Decimal('1.0')
    
    @staticmethod
    def calculate_demand_factor():
        demand_levels = {
            'LOW': Decimal('1.0'),
            'MEDIUM': Decimal('1.15'),
            'HIGH': Decimal('1.3')
        }
        current_demand = random.choice(['LOW', 'MEDIUM', 'HIGH'])
        return demand_levels[current_demand], current_demand
    
    @classmethod
    def calculate_dynamic_fare(cls, flight):
        base_fare = flight.base_fare
        
        seat_factor = cls.calculate_seat_factor(
            flight.seats_available, 
            flight.total_seats
        )
        
        time_factor = cls.calculate_time_factor(flight.departure_time)
        demand_factor, demand_level = cls.calculate_demand_factor()
        
        dynamic_fare = base_fare * seat_factor * time_factor * demand_factor
        
        return {
            'base_fare': base_fare,
            'dynamic_fare': round(dynamic_fare, 2),
            'seat_factor': seat_factor,
            'time_factor': time_factor,
            'demand_factor': demand_factor,
            'demand_level': demand_level
        }
```

2. **Enhanced Flight Serializer** (flights/serializers.py)
```python
from rest_framework import serializers
from .models import Flight, Airline, Airport
from .services.pricing import PricingEngine

class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = ['name', 'code']

class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ['iata_code', 'name', 'city']

class FlightSerializer(serializers.ModelSerializer):
    airline = AirlineSerializer(read_only=True)
    origin = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)
    pricing_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Flight
        fields = [
            'id', 'flight_no', 'airline', 'origin', 'destination',
            'departure_time', 'arrival_time', 'base_fare', 'seats_available',
            'total_seats', 'aircraft_type', 'pricing_details'
        ]
    
    def get_pricing_details(self, obj):
        return PricingEngine.calculate_dynamic_fare(obj)
```

#### Deliverables
- Dynamic pricing engine with multiple factors
- Real-time fare calculation in search results
- Fare history tracking system
- Demand simulation mechanism

### MILESTONE 3: Booking Workflow & Transaction Management (Weeks 5-6)

#### Objectives
- Implement complete booking workflow
- Add concurrency control for seat reservations
- Generate unique PNR codes
- Handle payment simulation
- Create booking management APIs

#### Implementation Steps

1. **Booking Models** (bookings/models.py)
```python
from django.db import models
from flights.models import Flight
import string
import random

class Booking(models.Model):
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('PENDING', 'Pending'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending'),
    ]
    
    pnr = models.CharField(max_length=10, unique=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    passenger_name = models.CharField(max_length=200)
    passenger_age = models.IntegerField()
    passenger_phone = models.CharField(max_length=15)
    passenger_email = models.EmailField(blank=True)
    seat_number = models.CharField(max_length=5)
    booking_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    final_fare = models.DecimalField(max_digits=10, decimal_places=2)
    booking_time = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    
    @staticmethod
    def generate_pnr():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def save(self, *args, **kwargs):
        if not self.pnr:
            self.pnr = self.generate_pnr()
            while Booking.objects.filter(pnr=self.pnr).exists():
                self.pnr = self.generate_pnr()
        super().save(*args, **kwargs)
```

2. **Booking Service** (bookings/services/booking.py)
```python
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import Booking
from flights.services.pricing import PricingEngine
import random

class BookingService:
    @staticmethod
    def create_booking(flight, passenger_data, seat_number):
        try:
            with transaction.atomic():
                # Lock the flight row for update
                flight = Flight.objects.select_for_update().get(id=flight.id)
                
                # Check seat availability
                if flight.seats_available <= 0:
                    raise ValidationError("No seats available")
                
                # Calculate final fare
                pricing_details = PricingEngine.calculate_dynamic_fare(flight)
                final_fare = pricing_details['dynamic_fare']
                
                # Simulate payment
                payment_success = BookingService.simulate_payment()
                
                if not payment_success:
                    raise ValidationError("Payment failed")
                
                # Create booking
                booking = Booking.objects.create(
                    flight=flight,
                    passenger_name=passenger_data['name'],
                    passenger_age=passenger_data['age'],
                    passenger_phone=passenger_data['phone'],
                    passenger_email=passenger_data.get('email', ''),
                    seat_number=seat_number,
                    final_fare=final_fare,
                    booking_status='CONFIRMED',
                    payment_status='SUCCESS'
                )
                
                # Update seat availability
                flight.seats_available -= 1
                flight.save()
                
                return booking
                
        except Exception as e:
            raise ValidationError(f"Booking failed: {str(e)}")
    
    @staticmethod
    def simulate_payment():
        # 90% success rate for simulation
        return random.random() < 0.9
    
    @staticmethod
    def cancel_booking(pnr):
        try:
            with transaction.atomic():
                booking = Booking.objects.select_for_update().get(
                    pnr=pnr, 
                    booking_status='CONFIRMED'
                )
                
                # Update booking status
                booking.booking_status = 'CANCELLED'
                booking.save()
                
                # Return seat to inventory
                flight = booking.flight
                flight.seats_available += 1
                flight.save()
                
                return booking
                
        except Booking.DoesNotExist:
            raise ValidationError("Booking not found or already cancelled")
```

3. **Booking APIs** (bookings/views.py)
```python
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from flights.models import Flight
from .services.booking import BookingService
from .serializers import BookingSerializer

@api_view(['POST'])
def create_booking(request):
    try:
        flight_id = request.data.get('flight_id')
        passenger_data = request.data.get('passenger')
        seat_number = request.data.get('seat_number')
        
        flight = get_object_or_404(Flight, id=flight_id)
        
        booking = BookingService.create_booking(
            flight, passenger_data, seat_number
        )
        
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except ValidationError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['DELETE'])
def cancel_booking(request, pnr):
    try:
        booking = BookingService.cancel_booking(pnr)
        return Response(
            {'message': 'Booking cancelled successfully'}, 
            status=status.HTTP_200_OK
        )
    except ValidationError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
def get_booking(request, pnr):
    booking = get_object_or_404(Booking, pnr=pnr)
    serializer = BookingSerializer(booking)
    return Response(serializer.data)
```

#### Deliverables
- Complete booking workflow with validation
- Concurrency-safe seat reservation system
- PNR generation and management
- Payment simulation with success/failure handling
- Booking cancellation functionality

### MILESTONE 4: User Interface & API Integration (Weeks 7-8)

#### Objectives
- Create responsive web interface
- Integrate all backend APIs
- Implement booking flow UI
- Add receipt generation and download
- Final testing and polish

#### Implementation Steps

1. **Frontend Structure**
```
templates/
├── base.html
├── flights/
│   ├── search.html
│   ├── results.html
│   └── details.html
├── bookings/
│   ├── form.html
│   ├── confirmation.html
│   └── receipt.html
└── includes/
    ├── navbar.html
    └── footer.html

static/
├── css/
│   ├── bootstrap.min.css
│   └── custom.css
├── js/
│   ├── bootstrap.min.js
│   ├── search.js
│   └── booking.js
└── images/
```

2. **Search Interface** (templates/flights/search.html)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flight Search - Flight Booking Simulator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h3 class="text-center">Search Flights</h3>
                    </div>
                    <div class="card-body">
                        <form id="searchForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="origin" class="form-label">From</label>
                                    <select class="form-select" id="origin" required>
                                        <option value="">Select Origin</option>
                                        <option value="DEL">Delhi (DEL)</option>
                                        <option value="BOM">Mumbai (BOM)</option>
                                        <option value="BLR">Bangalore (BLR)</option>
                                        <option value="MAA">Chennai (MAA)</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="destination" class="form-label">To</label>
                                    <select class="form-select" id="destination" required>
                                        <option value="">Select Destination</option>
                                        <option value="DEL">Delhi (DEL)</option>
                                        <option value="BOM">Mumbai (BOM)</option>
                                        <option value="BLR">Bangalore (BLR)</option>
                                        <option value="MAA">Chennai (MAA)</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="date" class="form-label">Departure Date</label>
                                    <input type="date" class="form-control" id="date" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="sortBy" class="form-label">Sort By</label>
                                    <select class="form-select" id="sortBy">
                                        <option value="departure_time">Departure Time</option>
                                        <option value="base_fare">Price</option>
                                        <option value="arrival_time">Arrival Time</option>
                                    </select>
                                </div>
                            </div>
                            <div class="text-center">
                                <button type="submit" class="btn btn-primary btn-lg">Search Flights</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Results Section -->
        <div id="resultsSection" class="mt-5" style="display: none;">
            <h4>Available Flights</h4>
            <div id="flightResults"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{% static 'js/search.js' %}"></script>
</body>
</html>
```

3. **Search JavaScript** (static/js/search.js)
```javascript
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const resultsSection = document.getElementById('resultsSection');
    const flightResults = document.getElementById('flightResults');

    // Set minimum date to today
    const dateInput = document.getElementById('date');
    const today = new Date().toISOString().split('T')[0];
    dateInput.min = today;
    dateInput.value = today;

    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        searchFlights();
    });

    async function searchFlights() {
        const formData = new FormData(searchForm);
        const params = new URLSearchParams();
        
        params.append('origin__iata_code', formData.get('origin'));
        params.append('destination__iata_code', formData.get('destination'));
        params.append('date', formData.get('date'));
        params.append('ordering', formData.get('sortBy'));

        try {
            const response = await fetch(`/api/flights/search/?${params}`);
            const data = await response.json();
            
            displayResults(data.results || data);
        } catch (error) {
            console.error('Error searching flights:', error);
            alert('Error searching flights. Please try again.');
        }
    }

    function displayResults(flights) {
        if (flights.length === 0) {
            flightResults.innerHTML = '<div class="alert alert-info">No flights found for the selected criteria.</div>';
        } else {
            flightResults.innerHTML = flights.map(flight => createFlightCard(flight)).join('');
        }
        
        resultsSection.style.display = 'block';
    }

    function createFlightCard(flight) {
        const pricing = flight.pricing_details;
        const departureTime = new Date(flight.departure_time).toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit'
        });
        const arrivalTime = new Date(flight.arrival_time).toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit'
        });

        return `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-2">
                            <h6 class="mb-0">${flight.airline.name}</h6>
                            <small class="text-muted">${flight.flight_no}</small>
                        </div>
                        <div class="col-md-3">
                            <div class="d-flex align-items-center">
                                <div class="text-center">
                                    <h5 class="mb-0">${departureTime}</h5>
                                    <small>${flight.origin.iata_code}</small>
                                </div>
                                <div class="mx-3">
                                    <i class="fas fa-plane text-primary"></i>
                                </div>
                                <div class="text-center">
                                    <h5 class="mb-0">${arrivalTime}</h5>
                                    <small>${flight.destination.iata_code}</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <small class="text-muted">Seats Available</small>
                            <h6 class="mb-0">${flight.seats_available}</h6>
                        </div>
                        <div class="col-md-3">
                            <div class="text-end">
                                <small class="text-muted">Base: ₹${pricing.base_fare}</small>
                                <h4 class="mb-0 text-primary">₹${pricing.dynamic_fare}</h4>
                                <small class="text-success">Demand: ${pricing.demand_level}</small>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <button class="btn btn-primary w-100" onclick="selectFlight(${flight.id})">
                                Select
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    window.selectFlight = function(flightId) {
        window.location.href = `/booking/create/?flight_id=${flightId}`;
    };
});
```

4. **Booking Form** (templates/bookings/form.html)
```html
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h3>Complete Your Booking</h3>
                </div>
                <div class="card-body">
                    <!-- Flight Details -->
                    <div class="alert alert-info">
                        <h5>Flight Details</h5>
                        <p><strong>{{ flight.airline.name }}</strong> - {{ flight.flight_no }}</p>
                        <p>{{ flight.origin.name }} → {{ flight.destination.name }}</p>
                        <p>{{ flight.departure_time|date:"M d, Y H:i" }} - {{ flight.arrival_time|date:"H:i" }}</p>
                        <p><strong>Fare: ₹{{ pricing_details.dynamic_fare }}</strong></p>
                    </div>

                    <form id="bookingForm">
                        <input type="hidden" id="flightId" value="{{ flight.id }}">
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="passengerName" class="form-label">Full Name</label>
                                <input type="text" class="form-control" id="passengerName" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="passengerAge" class="form-label">Age</label>
                                <input type="number" class="form-control" id="passengerAge" min="1" max="120" required>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="passengerPhone" class="form-label">Phone Number</label>
                                <input type="tel" class="form-control" id="passengerPhone" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="passengerEmail" class="form-label">Email</label>
                                <input type="email" class="form-control" id="passengerEmail">
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="seatNumber" class="form-label">Seat Number</label>
                            <select class="form-select" id="seatNumber" required>
                                <option value="">Select Seat</option>
                                <!-- Seat options would be dynamically generated -->
                                {% for seat in available_seats %}
                                <option value="{{ seat }}">{{ seat }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div class="text-center">
                            <button type="submit" class="btn btn-success btn-lg">
                                Proceed to Payment
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.getElementById('bookingForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const bookingData = {
        flight_id: document.getElementById('flightId').value,
        passenger: {
            name: document.getElementById('passengerName').value,
            age: parseInt(document.getElementById('passengerAge').value),
            phone: document.getElementById('passengerPhone').value,
            email: document.getElementById('passengerEmail').value
        },
        seat_number: document.getElementById('seatNumber').value
    };
    
    try {
        const response = await fetch('/api/bookings/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(bookingData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            window.location.href = `/booking/confirmation/${result.pnr}/`;
        } else {
            alert('Booking failed: ' + result.error);
        }
    } catch (error) {
        alert('Booking failed. Please try again.');
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
</script>
```

#### Deliverables
- Complete responsive web interface
- Integrated flight search and booking flow
- Real-time price display with dynamic updates
- Booking confirmation and PNR display
- Receipt generation and download functionality

## PART 6 — API ENDPOINTS SUMMARY

### Flight APIs
- `GET /api/flights/search/` - Search flights with filters
- `GET /api/flights/<id>/` - Get flight details
- `GET /api/airports/` - List all airports
- `GET /api/airlines/` - List all airlines

### Booking APIs  
- `POST /api/bookings/create/` - Create new booking
- `GET /api/bookings/<pnr>/` - Get booking details
- `DELETE /api/bookings/<pnr>/cancel/` - Cancel booking
- `GET /api/bookings/<pnr>/receipt/` - Download receipt

### Admin APIs
- `GET /api/admin/bookings/` - List all bookings
- `GET /api/admin/flights/` - Manage flights
- `GET /api/admin/analytics/` - Booking analytics

## PART 7 — DEPLOYMENT & PRODUCTION CONSIDERATIONS

### Environment Setup
```bash
# Production settings
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'flight_booking_prod',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Security Measures
- CSRF protection on all forms
- Input validation and sanitization
- Rate limiting on search APIs
- SQL injection prevention through ORM
- XSS protection in templates

### Performance Optimization
- Database indexing on frequently queried fields
- Query optimization with select_related()
- Caching for static data (airports, airlines)
- Connection pooling for database
- CDN for static assets

### Scalability Considerations
- Horizontal scaling with load balancers
- Database read replicas for search queries
- Redis for session management and caching
- Microservices architecture for large scale
- API rate limiting and throttling

## PART 8 — TESTING STRATEGY

### Unit Tests
- Model validation tests
- Service layer logic tests
- API endpoint tests
- Pricing algorithm tests

### Integration Tests
- End-to-end booking flow
- Concurrency testing for seat booking
- Payment simulation testing
- Database transaction testing

### Performance Tests
- Load testing for search APIs
- Stress testing for concurrent bookings
- Database performance under load
- Frontend responsiveness testing

## CONCLUSION

This Flight Booking Simulator demonstrates a complete full-stack application with:

- **Robust Backend Architecture**: Django with proper separation of concerns
- **Dynamic Business Logic**: Sophisticated pricing algorithms
- **Data Integrity**: ACID transactions and concurrency control
- **Modern Frontend**: Responsive UI with real-time updates
- **Production Ready**: Security, performance, and scalability considerations

The project showcases enterprise-level development practices including proper database design, API development, transaction management, and user experience design. It serves as an excellent demonstration of full-stack development capabilities and understanding of complex business logic implementation.

**Key Technical Achievements:**
- Implemented complex pricing algorithms with multiple factors
- Achieved concurrency-safe booking system using database transactions
- Created responsive and intuitive user interface
- Designed scalable and maintainable code architecture
- Integrated multiple technologies into cohesive system

This project is suitable for portfolio demonstration, technical interviews, and as a foundation for real-world airline booking systems.