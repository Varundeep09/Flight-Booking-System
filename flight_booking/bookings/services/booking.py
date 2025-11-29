from django.db import transaction
from ..models import Booking
import random
import string

def generate_pnr():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def create_booking(flight, passenger_name, phone, seat):
    with transaction.atomic():
        # Check if seat is available
        if flight.seats <= 0:
            return None, "No seats available"
        
        # Generate PNR
        pnr = generate_pnr()
        while Booking.objects.filter(pnr=pnr).exists():
            pnr = generate_pnr()
        
        # Create booking
        booking = Booking.objects.create(
            pnr=pnr,
            flight=flight,
            passenger_name=passenger_name,
            passenger_phone=phone,
            seat_number=seat,
            price=flight.price
        )
        
        # Update flight seats
        flight.seats -= 1
        flight.save()
        
        return booking, "Success"

def cancel_booking(pnr):
    try:
        booking = Booking.objects.get(pnr=pnr)
        booking.status = 'cancelled'
        booking.save()
        
        # Return seat to flight
        flight = booking.flight
        flight.seats += 1
        flight.save()
        
        return True
    except Booking.DoesNotExist:
        return False