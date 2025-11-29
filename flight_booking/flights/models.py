from django.db import models

class Airline(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3)
    
    def __str__(self):
        return self.name

class Airport(models.Model):
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.city} ({self.code})"

class Flight(models.Model):
    flight_no = models.CharField(max_length=10)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departures')
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrivals')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    seats = models.IntegerField()
    
    def __str__(self):
        return f"{self.flight_no} - {self.origin.code} to {self.destination.code}"