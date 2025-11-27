"""
Booking models for the flight reservation system.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from flights.models import Flight
import string
import random


class Booking(models.Model):
    """
    Booking model to store passenger reservations.
    """
    
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
    
    pnr = models.CharField(
        max_length=10, 
        unique=True, 
        help_text="Passenger Name Record - unique booking reference"
    )
    flight = models.ForeignKey(
        Flight, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        help_text="Associated flight"
    )
    passenger_name = models.CharField(
        max_length=200, 
        help_text="Full name of passenger"
    )
    passenger_age = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        help_text="Age of passenger"
    )
    passenger_phone = models.CharField(
        max_length=15, 
        help_text="Contact phone number"
    )
    passenger_email = models.EmailField(
        blank=True, 
        help_text="Email address (optional)"
    )
    seat_number = models.CharField(
        max_length=5, 
        help_text="Assigned seat number (e.g., 12A)"
    )
    booking_status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='PENDING',
        help_text="Current booking status"
    )
    final_fare = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Final amount paid for the booking"
    )
    booking_time = models.DateTimeField(
        auto_now_add=True,
        help_text="When the booking was created"
    )
    payment_status = models.CharField(
        max_length=10, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='PENDING',
        help_text="Payment processing status"
    )
    
    # Additional booking details
    booking_reference = models.CharField(
        max_length=20,
        blank=True,
        help_text="External booking reference (if any)"
    )
    special_requests = models.TextField(
        blank=True,
        help_text="Special meal, assistance, etc."
    )
    
    class Meta:
        db_table = 'bookings'
        ordering = ['-booking_time']
        indexes = [
            models.Index(fields=['pnr']),
            models.Index(fields=['flight', 'booking_status']),
            models.Index(fields=['passenger_phone']),
            models.Index(fields=['booking_time']),
        ]
    
    @staticmethod
    def generate_pnr():
        """Generate a unique PNR code."""
        # Format: 2 letters + 4 digits (e.g., AB1234)
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        digits = ''.join(random.choices(string.digits, k=4))
        return letters + digits
    
    def save(self, *args, **kwargs):
        """Override save to generate PNR if not provided."""
        if not self.pnr:
            self.pnr = self.generate_pnr()
            # Ensure uniqueness
            while Booking.objects.filter(pnr=self.pnr).exists():
                self.pnr = self.generate_pnr()
        
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        """Check if booking is active (confirmed and not cancelled)."""
        return self.booking_status == 'CONFIRMED' and self.payment_status == 'SUCCESS'
    
    @property
    def can_be_cancelled(self):
        """Check if booking can be cancelled."""
        from django.utils import timezone
        
        if self.booking_status != 'CONFIRMED':
            return False
        
        # Allow cancellation up to 2 hours before departure
        time_until_departure = self.flight.departure_time - timezone.now()
        return time_until_departure.total_seconds() > 7200  # 2 hours
    
    @property
    def total_amount_formatted(self):
        """Return formatted total amount."""
        return f"₹{self.final_fare:,.2f}"
    
    def __str__(self):
        return f"PNR: {self.pnr} - {self.passenger_name} on {self.flight.flight_no}"


class BookingHistory(models.Model):
    """
    Model to track booking status changes and modifications.
    """
    
    ACTION_CHOICES = [
        ('CREATED', 'Booking Created'),
        ('CONFIRMED', 'Booking Confirmed'),
        ('CANCELLED', 'Booking Cancelled'),
        ('MODIFIED', 'Booking Modified'),
        ('PAYMENT_SUCCESS', 'Payment Successful'),
        ('PAYMENT_FAILED', 'Payment Failed'),
    ]
    
    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='history'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    performed_at = models.DateTimeField(auto_now_add=True)
    performed_by = models.CharField(
        max_length=100, 
        default='system',
        help_text="Who performed the action"
    )
    
    class Meta:
        db_table = 'booking_history'
        ordering = ['-performed_at']
        verbose_name_plural = 'Booking histories'
    
    def __str__(self):
        return f"{self.booking.pnr} - {self.action} at {self.performed_at}"


class PaymentTransaction(models.Model):
    """
    Model to track payment transactions for bookings.
    """
    
    TRANSACTION_STATUS_CHOICES = [
        ('INITIATED', 'Initiated'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
        ('PENDING', 'Pending'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('NET_BANKING', 'Net Banking'),
        ('UPI', 'UPI'),
        ('WALLET', 'Digital Wallet'),
    ]
    
    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    transaction_id = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Unique transaction identifier"
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Transaction amount"
    )
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES,
        default='CREDIT_CARD'
    )
    status = models.CharField(
        max_length=10, 
        choices=TRANSACTION_STATUS_CHOICES, 
        default='INITIATED'
    )
    gateway_response = models.JSONField(
        blank=True, 
        null=True,
        help_text="Payment gateway response data"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_transactions'
        ordering = ['-created_at']
    
    @staticmethod
    def generate_transaction_id():
        """Generate unique transaction ID."""
        import uuid
        return str(uuid.uuid4())[:12].upper()
    
    def save(self, *args, **kwargs):
        """Override save to generate transaction ID."""
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
            while PaymentTransaction.objects.filter(
                transaction_id=self.transaction_id
            ).exists():
                self.transaction_id = self.generate_transaction_id()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - ₹{self.amount} ({self.status})"