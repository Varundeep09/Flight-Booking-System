"""
Views for flight-related functionality.
"""
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import datetime

from .models import Flight, Airline, Airport, FareHistory
from .serializers import (
    FlightListSerializer, FlightDetailSerializer, FlightSearchSerializer,
    AirlineSerializer, AirportSerializer, FareHistorySerializer
)
from .services.pricing import PricingEngine


class FlightSearchView(generics.ListAPIView):
    """
    API view for searching flights with dynamic pricing.
    
    Supports filtering by:
    - Origin and destination airports
    - Departure date
    - Price range
    - Airline
    
    Supports sorting by:
    - Departure time
    - Price (base or dynamic)
    - Duration
    """
    
    serializer_class = FlightListSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['airline__code', 'status']
    ordering_fields = ['departure_time', 'arrival_time', 'base_fare']
    ordering = ['departure_time']
    
    def get_queryset(self):
        """Filter flights based on search parameters."""
        queryset = Flight.objects.select_related(
            'airline', 'origin', 'destination'
        ).filter(
            status='SCHEDULED',
            seats_available__gt=0,
            departure_time__gt=timezone.now()
        )
        
        # Apply search filters
        origin = self.request.query_params.get('origin')
        destination = self.request.query_params.get('destination')
        date = self.request.query_params.get('date')
        max_price = self.request.query_params.get('max_price')
        airline = self.request.query_params.get('airline')
        
        if origin:
            queryset = queryset.filter(origin__iata_code__iexact=origin)
        
        if destination:
            queryset = queryset.filter(destination__iata_code__iexact=destination)
        
        if date:
            try:
                search_date = datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(departure_time__date=search_date)
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        if airline:
            queryset = queryset.filter(airline__code__iexact=airline)
        
        # Note: max_price filtering is applied after dynamic pricing calculation
        # This is handled in the list method
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Override list to handle dynamic price filtering."""
        queryset = self.get_queryset()
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            flights_data = serializer.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            flights_data = serializer.data
        
        # Apply max_price filter after dynamic pricing calculation
        max_price = request.query_params.get('max_price')
        if max_price:
            try:
                max_price_value = float(max_price)
                flights_data = [
                    flight for flight in flights_data
                    if flight['pricing_details']['dynamic_fare'] <= max_price_value
                ]
            except (ValueError, KeyError):
                pass  # Invalid price or missing pricing data
        
        # Apply dynamic price sorting if requested
        sort_by = request.query_params.get('sort_by', 'departure_time')
        sort_order = request.query_params.get('sort_order', 'asc')
        
        if sort_by == 'dynamic_fare':
            reverse_order = sort_order == 'desc'
            flights_data.sort(
                key=lambda x: x['pricing_details']['dynamic_fare'],
                reverse=reverse_order
            )
        
        if page is not None:
            return self.get_paginated_response(flights_data)
        
        return Response(flights_data)


class FlightDetailView(generics.RetrieveAPIView):
    """
    API view for retrieving detailed flight information.
    Includes comprehensive pricing details and analytics.
    """
    
    queryset = Flight.objects.select_related('airline', 'origin', 'destination')
    serializer_class = FlightDetailSerializer
    lookup_field = 'id'


class AirlineListView(generics.ListAPIView):
    """API view for listing all airlines."""
    
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    ordering = ['name']


class AirportListView(generics.ListAPIView):
    """API view for listing all airports."""
    
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['iata_code', 'name', 'city']
    ordering = ['city', 'name']


class FareHistoryView(generics.ListAPIView):
    """API view for fare history analytics."""
    
    serializer_class = FareHistorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['flight__id', 'demand_level']
    ordering = ['-recorded_at']
    
    def get_queryset(self):
        """Filter fare history by flight or date range."""
        queryset = FareHistory.objects.select_related('flight')
        
        flight_id = self.request.query_params.get('flight_id')
        if flight_id:
            queryset = queryset.filter(flight__id=flight_id)
        
        days = self.request.query_params.get('days', 7)
        try:
            days = int(days)
            from datetime import timedelta
            start_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(recorded_at__gte=start_date)
        except ValueError:
            pass
        
        return queryset


@api_view(['POST'])
def validate_search(request):
    """
    Validate flight search parameters.
    """
    serializer = FlightSearchSerializer(data=request.data)
    if serializer.is_valid():
        return Response({
            'valid': True,
            'data': serializer.validated_data
        })
    else:
        return Response({
            'valid': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def flight_analytics(request):
    """
    Get flight analytics and statistics.
    """
    from django.db.models import Avg, Count, Sum
    
    # Basic statistics
    total_flights = Flight.objects.filter(status='SCHEDULED').count()
    total_airlines = Airline.objects.count()
    total_airports = Airport.objects.count()
    
    # Occupancy statistics
    occupancy_stats = Flight.objects.filter(
        status='SCHEDULED'
    ).aggregate(
        avg_occupancy=Avg('total_seats') - Avg('seats_available'),
        total_capacity=Sum('total_seats'),
        total_available=Sum('seats_available')
    )
    
    # Popular routes
    popular_routes = Flight.objects.filter(
        status='SCHEDULED'
    ).values(
        'origin__iata_code',
        'origin__city',
        'destination__iata_code',
        'destination__city'
    ).annotate(
        flight_count=Count('id')
    ).order_by('-flight_count')[:10]
    
    # Airline statistics
    airline_stats = Airline.objects.annotate(
        flight_count=Count('flights', filter=Q(flights__status='SCHEDULED'))
    ).order_by('-flight_count')
    
    return Response({
        'summary': {
            'total_flights': total_flights,
            'total_airlines': total_airlines,
            'total_airports': total_airports,
            'average_occupancy_rate': round(
                (occupancy_stats['avg_occupancy'] or 0) / 
                (occupancy_stats['total_capacity'] / total_flights if total_flights > 0 else 1) * 100, 2
            ) if total_flights > 0 else 0
        },
        'popular_routes': list(popular_routes),
        'airline_stats': AirlineSerializer(airline_stats, many=True).data
    })


# Frontend Views (Django Templates)

def search_flights_page(request):
    """Render flight search page."""
    airports = Airport.objects.all().order_by('city')
    airlines = Airline.objects.all().order_by('name')
    
    context = {
        'airports': airports,
        'airlines': airlines,
        'today': timezone.now().date()
    }
    return render(request, 'flights/search.html', context)


def flight_results_page(request):
    """Render flight search results page."""
    # Get search parameters
    origin = request.GET.get('origin')
    destination = request.GET.get('destination')
    date = request.GET.get('date')
    
    flights = []
    if origin and destination and date:
        try:
            search_date = datetime.strptime(date, '%Y-%m-%d').date()
            flights = Flight.objects.select_related(
                'airline', 'origin', 'destination'
            ).filter(
                origin__iata_code__iexact=origin,
                destination__iata_code__iexact=destination,
                departure_time__date=search_date,
                status='SCHEDULED',
                seats_available__gt=0
            ).order_by('departure_time')
            
            # Add pricing details to each flight
            for flight in flights:
                flight.pricing_details = PricingEngine.calculate_dynamic_fare(flight)
                
        except ValueError:
            pass  # Invalid date format
    
    context = {
        'flights': flights,
        'search_params': {
            'origin': origin,
            'destination': destination,
            'date': date
        }
    }
    return render(request, 'flights/results.html', context)


def flight_detail_page(request, flight_id):
    """Render detailed flight information page."""
    flight = get_object_or_404(Flight, id=flight_id)
    pricing_details = PricingEngine.calculate_dynamic_fare(flight)
    fare_trends = PricingEngine.get_fare_trends(flight, days=7)
    
    context = {
        'flight': flight,
        'pricing_details': pricing_details,
        'fare_trends': list(fare_trends)
    }
    return render(request, 'flights/detail.html', context)