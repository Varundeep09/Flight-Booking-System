from rest_framework import generics
from rest_framework.response import Response
from .models import Flight
from django.http import JsonResponse

class FlightListView(generics.ListAPIView):
    queryset = Flight.objects.all()
    
    def get(self, request):
        flights = Flight.objects.all()
        data = []
        for flight in flights:
            data.append({
                'id': flight.id,
                'flight_no': flight.flight_no,
                'origin': flight.origin.code,
                'destination': flight.destination.code,
                'price': float(flight.price),
                'seats': flight.seats
            })
        return JsonResponse(data, safe=False)

def search_flights(request):
    origin = request.GET.get('origin')
    destination = request.GET.get('destination')
    
    flights = Flight.objects.filter(
        origin__code=origin,
        destination__code=destination
    )
    
    data = []
    for flight in flights:
        data.append({
            'flight_no': flight.flight_no,
            'price': float(flight.price),
            'seats': flight.seats
        })
    
    return JsonResponse(data, safe=False)