from django.db import models
from flights.models import Flight

class Booking(models.Model):
    pnr = models.CharField(max_length=10, unique=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    passenger_name = models.CharField(max_length=100)
    passenger_phone = models.CharField(max_length=15)
    seat_number = models.CharField(max_length=5)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.pnr} - {self.passenger_name}"