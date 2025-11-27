"""
Flight models for the booking system.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Airline(models.Model):
    """Airline model to store airline information."""
    name = models.CharField(max_length=100, help_text="Full airline name")
    code = models.CharField(max_length=3, unique=True, help_text="IATA airline code")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'airlines'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Airport(models.Model):
    """Airport model to store airport information."""
    iata_code = models.CharField(max_length=3, unique=True, help_text="IATA airport code")
    name = models.CharField(max_length=200, help_text="Full airport name")
    city = models.CharField(max_length=100, help_text="City name")
    country = models.CharField(max_length=100, default='India', help_text="Country name")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'airports'
        ordering = ['city', 'name']

    def __str__(self):
        return f"{self.city} ({self.iata_code})"


class Flight(models.Model):
    """Flight model to store flight information."""
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('DELAYED', 'Delayed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    flight_no = models.CharField(max_length=10, unique=True, help_text="Flight number")
    airline = models.ForeignKey(
        Airline, 
        on_delete=models.CASCADE, 
        related_name='flights',
        help_text="Operating airline"
    )
    origin = models.ForeignKey(
        Airport, 
        on_delete=models.CASCADE, 
        related_name='departing_flights',
        help_text="Departure airport"
    )
    destination = models.ForeignKey(
        Airport, 
        on_delete=models.CASCADE, 
        related_name='arriving_flights',
        help_text="Arrival airport"
    )
    departure_time = models.DateTimeField(help_text="Scheduled departure time")
    arrival_time = models.DateTimeField(help_text="Scheduled arrival time")
    base_fare = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Base fare in INR"
    )
    total_seats = models.IntegerField(
        default=180,
        validators=[MinValueValidator(1), MaxValueValidator(500)],
        help_text="Total seats in aircraft"
    )
    seats_available = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Currently available seats"
    )
    aircraft_type = models.CharField(
        max_length=50, 
        blank=True, 
        default='Boeing 737',
        help_text="Aircraft model"
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='SCHEDULED',
        help_text="Current flight status"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'flights'
        ordering = ['departure_time']
        indexes = [
            models.Index(fields=['origin', 'destination', 'departure_time']),
            models.Index(fields=['departure_time']),
            models.Index(fields=['status']),
        ]

    def clean(self):
        """Validate flight data."""
        from django.core.exceptions import ValidationError
        
        if self.departure_time and self.arrival_time:
            if self.departure_time >= self.arrival_time:
                raise ValidationError('Departure time must be before arrival time.')
        
        if self.seats_available > self.total_seats:
            raise ValidationError('Available seats cannot exceed total seats.')
        
        if self.origin == self.destination:
            raise ValidationError('Origin and destination cannot be the same.')

    def save(self, *args, **kwargs):
        """Override save to set initial seats_available."""
        if not self.pk and not hasattr(self, '_seats_available_set'):
            self.seats_available = self.total_seats
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def duration(self):
        """Calculate flight duration."""
        if self.departure_time and self.arrival_time:
            return self.arrival_time - self.departure_time
        return None

    @property
    def occupancy_rate(self):
        """Calculate current occupancy rate."""
        if self.total_seats > 0:
            return (self.total_seats - self.seats_available) / self.total_seats
        return 0

    @property
    def is_available(self):
        """Check if flight is available for booking."""
        return (
            self.status == 'SCHEDULED' and 
            self.seats_available > 0 and 
            self.departure_time > timezone.now()
        )

    def __str__(self):
        return f"{self.flight_no} - {self.origin.iata_code} to {self.destination.iata_code}"


class FareHistory(models.Model):
    """Model to track fare changes for analytics."""
    
    DEMAND_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]
    
    flight = models.ForeignKey(
        Flight, 
        on_delete=models.CASCADE, 
        related_name='fare_history'
    )
    calculated_fare = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Dynamically calculated fare"
    )
    seats_remaining = models.IntegerField(help_text="Seats available at time of calculation")
    demand_level = models.CharField(
        max_length=6, 
        choices=DEMAND_CHOICES,
        help_text="Simulated demand level"
    )
    time_to_departure = models.IntegerField(help_text="Hours until departure")
    seat_factor = models.DecimalField(max_digits=3, decimal_places=2)
    time_factor = models.DecimalField(max_digits=3, decimal_places=2)
    demand_factor = models.DecimalField(max_digits=3, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fare_history'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['flight', 'recorded_at']),
            models.Index(fields=['demand_level']),
        ]

    def __str__(self):
        return f"{self.flight.flight_no} - ₹{self.calculated_fare} at {self.recorded_at}"