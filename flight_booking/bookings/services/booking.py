"""
Booking service for handling flight reservations with concurrency control.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from flights.models import Flight
from flights.services.pricing import PricingEngine
from ..models import Booking, BookingHistory, PaymentTransaction
import random
import logging

logger = logging.getLogger(__name__)


class BookingService:
    """
    Service class for handling flight bookings with concurrency safety.
    """
    
    @staticmethod
    def create_booking(flight_id, passenger_data, seat_number, payment_method='CREDIT_CARD'):
        """
        Create a new flight booking with concurrency control.
        
        Args:
            flight_id (int): ID of the flight to book
            passenger_data (dict): Passenger information
            seat_number (str): Selected seat number
            payment_method (str): Payment method choice
            
        Returns:
            Booking: Created booking instance
            
        Raises:
            ValidationError: If booking cannot be completed
        """
        try:
            with transaction.atomic():
                # Lock the flight row for update to prevent race conditions
                flight = Flight.objects.select_for_update().get(id=flight_id)
                
                # Validate flight availability
                if not flight.is_available:
                    raise ValidationError("Flight is not available for booking")
                
                if flight.seats_available <= 0:
                    raise ValidationError("No seats available on this flight")
                
                # Check if seat is already taken (in a real system, you'd have a seat map)
                existing_booking = Booking.objects.filter(
                    flight=flight,
                    seat_number=seat_number,
                    booking_status='CONFIRMED'
                ).exists()
                
                if existing_booking:
                    raise ValidationError(f"Seat {seat_number} is already booked")
                
                # Calculate final fare using dynamic pricing
                pricing_details = PricingEngine.calculate_dynamic_fare(flight)
                final_fare = pricing_details['dynamic_fare']
                
                # Create payment transaction
                payment_transaction = PaymentTransaction.objects.create(
                    booking=None,  # Will be set after booking creation
                    amount=final_fare,
                    payment_method=payment_method,
                    status='INITIATED'
                )
                
                # Simulate payment processing
                payment_success = BookingService._simulate_payment(payment_transaction)
                
                if not payment_success:
                    payment_transaction.status = 'FAILED'
                    payment_transaction.save()
                    raise ValidationError("Payment processing failed. Please try again.")
                
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
                    payment_status='SUCCESS',
                    special_requests=passenger_data.get('special_requests', '')
                )
                
                # Update payment transaction with booking reference
                payment_transaction.booking = booking
                payment_transaction.status = 'SUCCESS'
                payment_transaction.save()
                
                # Update flight seat availability
                flight.seats_available -= 1
                flight.save()
                
                # Create booking history entry
                BookingHistory.objects.create(
                    booking=booking,
                    action='CREATED',
                    description=f"Booking created for {passenger_data['name']} on flight {flight.flight_no}"
                )
                
                BookingHistory.objects.create(
                    booking=booking,
                    action='PAYMENT_SUCCESS',
                    description=f"Payment of ₹{final_fare} processed successfully"
                )
                
                logger.info(f"Booking created successfully: PNR {booking.pnr}")
                return booking
                
        except Flight.DoesNotExist:
            raise ValidationError("Flight not found")
        except Exception as e:
            logger.error(f"Booking creation failed: {str(e)}")
            raise ValidationError(f"Booking failed: {str(e)}")
    
    @staticmethod
    def _simulate_payment(payment_transaction):
        """
        Simulate payment processing with random success/failure.
        
        Args:
            payment_transaction (PaymentTransaction): Transaction to process
            
        Returns:
            bool: True if payment successful, False otherwise
        """
        # Simulate payment processing delay
        import time
        time.sleep(0.1)  # Simulate network delay
        
        # 90% success rate for simulation
        success = random.random() < 0.9
        
        # Simulate gateway response
        if success:
            payment_transaction.gateway_response = {
                'status': 'SUCCESS',
                'gateway_transaction_id': f"GW{random.randint(100000, 999999)}",
                'message': 'Payment processed successfully'
            }
        else:
            payment_transaction.gateway_response = {
                'status': 'FAILED',
                'error_code': 'INSUFFICIENT_FUNDS',
                'message': 'Payment declined by bank'
            }
        
        payment_transaction.save()
        return success
    
    @staticmethod
    def cancel_booking(pnr, reason='Customer request'):
        """
        Cancel an existing booking and return seat to inventory.
        
        Args:
            pnr (str): Booking PNR to cancel
            reason (str): Reason for cancellation
            
        Returns:
            Booking: Cancelled booking instance
            
        Raises:
            ValidationError: If booking cannot be cancelled
        """
        try:
            with transaction.atomic():
                # Lock booking for update
                booking = Booking.objects.select_for_update().get(
                    pnr=pnr,
                    booking_status='CONFIRMED'
                )
                
                # Check if booking can be cancelled
                if not booking.can_be_cancelled:
                    raise ValidationError(
                        "Booking cannot be cancelled. "
                        "Cancellation is allowed up to 2 hours before departure."
                    )
                
                # Update booking status
                booking.booking_status = 'CANCELLED'
                booking.save()
                
                # Return seat to flight inventory
                flight = booking.flight
                flight.seats_available += 1
                flight.save()
                
                # Create refund transaction
                refund_transaction = PaymentTransaction.objects.create(
                    booking=booking,
                    amount=-booking.final_fare,  # Negative amount for refund
                    payment_method=booking.transactions.first().payment_method,
                    status='SUCCESS'
                )
                
                # Create booking history entry
                BookingHistory.objects.create(
                    booking=booking,
                    action='CANCELLED',
                    description=f"Booking cancelled. Reason: {reason}"
                )
                
                logger.info(f"Booking cancelled successfully: PNR {booking.pnr}")
                return booking
                
        except Booking.DoesNotExist:
            raise ValidationError("Booking not found or already cancelled")
        except Exception as e:
            logger.error(f"Booking cancellation failed: {str(e)}")
            raise ValidationError(f"Cancellation failed: {str(e)}")
    
    @staticmethod
    def get_booking_details(pnr):
        """
        Retrieve comprehensive booking details.
        
        Args:
            pnr (str): Booking PNR
            
        Returns:
            dict: Comprehensive booking information
            
        Raises:
            ValidationError: If booking not found
        """
        try:
            booking = Booking.objects.select_related(
                'flight__airline',
                'flight__origin',
                'flight__destination'
            ).get(pnr=pnr)
            
            # Get current pricing for comparison
            current_pricing = PricingEngine.calculate_dynamic_fare(booking.flight)
            
            # Get booking history
            history = booking.history.all()
            
            # Get payment transactions
            transactions = booking.transactions.all()
            
            return {
                'booking': booking,
                'current_pricing': current_pricing,
                'price_difference': current_pricing['dynamic_fare'] - float(booking.final_fare),
                'history': history,
                'transactions': transactions,
                'can_cancel': booking.can_be_cancelled
            }
            
        except Booking.DoesNotExist:
            raise ValidationError("Booking not found")
    
    @staticmethod
    def generate_seat_map(flight, booked_seats=None):
        """
        Generate available seats for a flight.
        
        Args:
            flight (Flight): Flight instance
            booked_seats (list): Already booked seats
            
        Returns:
            dict: Seat map with availability
        """
        if booked_seats is None:
            booked_seats = list(
                Booking.objects.filter(
                    flight=flight,
                    booking_status='CONFIRMED'
                ).values_list('seat_number', flat=True)
            )
        
        # Generate seat map (simplified - 6 seats per row, A-F)
        seat_map = {
            'economy': [],
            'business': []
        }
        
        # Business class (rows 1-5)
        for row in range(1, 6):
            for seat_letter in ['A', 'B', 'C', 'D']:
                seat_number = f"{row}{seat_letter}"
                seat_map['business'].append({
                    'number': seat_number,
                    'available': seat_number not in booked_seats,
                    'type': 'business'
                })
        
        # Economy class (rows 6-30)
        for row in range(6, 31):
            for seat_letter in ['A', 'B', 'C', 'D', 'E', 'F']:
                seat_number = f"{row}{seat_letter}"
                seat_map['economy'].append({
                    'number': seat_number,
                    'available': seat_number not in booked_seats,
                    'type': 'economy'
                })
        
        return seat_map
    
    @staticmethod
    def validate_passenger_data(passenger_data):
        """
        Validate passenger information.
        
        Args:
            passenger_data (dict): Passenger information
            
        Returns:
            dict: Validated passenger data
            
        Raises:
            ValidationError: If validation fails
        """
        required_fields = ['name', 'age', 'phone']
        
        for field in required_fields:
            if not passenger_data.get(field):
                raise ValidationError(f"{field.title()} is required")
        
        # Validate age
        try:
            age = int(passenger_data['age'])
            if age < 1 or age > 120:
                raise ValidationError("Age must be between 1 and 120")
        except (ValueError, TypeError):
            raise ValidationError("Invalid age format")
        
        # Validate phone number
        phone = passenger_data['phone'].strip()
        if len(phone) < 10:
            raise ValidationError("Phone number must be at least 10 digits")
        
        # Validate name
        name = passenger_data['name'].strip()
        if len(name) < 2:
            raise ValidationError("Name must be at least 2 characters")
        
        return {
            'name': name.title(),
            'age': age,
            'phone': phone,
            'email': passenger_data.get('email', '').strip(),
            'special_requests': passenger_data.get('special_requests', '').strip()
        }