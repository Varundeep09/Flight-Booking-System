"""
Serializers for flight-related models and APIs.
"""
from rest_framework import serializers
from .models import Flight, Airline, Airport, FareHistory
from .services.pricing import PricingEngine


class AirlineSerializer(serializers.ModelSerializer):
    """Serializer for Airline model."""
    
    class Meta:
        model = Airline
        fields = ['id', 'name', 'code']


class AirportSerializer(serializers.ModelSerializer):
    """Serializer for Airport model."""
    
    class Meta:
        model = Airport
        fields = ['id', 'iata_code', 'name', 'city', 'country']


class FlightListSerializer(serializers.ModelSerializer):
    """Serializer for flight list view with dynamic pricing."""
    
    airline = AirlineSerializer(read_only=True)
    origin = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)
    pricing_details = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    is_available = serializers.ReadOnlyField()
    
    class Meta:
        model = Flight
        fields = [
            'id', 'flight_no', 'airline', 'origin', 'destination',
            'departure_time', 'arrival_time', 'base_fare', 'seats_available',
            'total_seats', 'aircraft_type', 'status', 'pricing_details',
            'duration', 'is_available'
        ]
    
    def get_pricing_details(self, obj):
        """Calculate and return dynamic pricing details."""
        return PricingEngine.calculate_dynamic_fare(obj, save_history=False)
    
    def get_duration(self, obj):
        """Return flight duration in a readable format."""
        if obj.duration:
            total_seconds = int(obj.duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return None


class FlightDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual flight view."""
    
    airline = AirlineSerializer(read_only=True)
    origin = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)
    pricing_details = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    occupancy_rate = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()
    fare_trends = serializers.SerializerMethodField()
    price_projections = serializers.SerializerMethodField()
    
    class Meta:
        model = Flight
        fields = [
            'id', 'flight_no', 'airline', 'origin', 'destination',
            'departure_time', 'arrival_time', 'base_fare', 'seats_available',
            'total_seats', 'aircraft_type', 'status', 'pricing_details',
            'duration', 'occupancy_rate', 'is_available', 'fare_trends',
            'price_projections', 'created_at'
        ]
    
    def get_pricing_details(self, obj):
        """Calculate and return comprehensive pricing details."""
        return PricingEngine.calculate_dynamic_fare(obj, save_history=True)
    
    def get_duration(self, obj):
        """Return flight duration in a readable format."""
        if obj.duration:
            total_seconds = int(obj.duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return {
                'hours': hours,
                'minutes': minutes,
                'formatted': f"{hours}h {minutes}m",
                'total_minutes': total_seconds // 60
            }
        return None
    
    def get_fare_trends(self, obj):
        """Get recent fare trends for this flight."""
        return list(PricingEngine.get_fare_trends(obj, days=7))
    
    def get_price_projections(self, obj):
        """Get price projections for the next 24 hours."""
        return PricingEngine.simulate_price_changes(obj, hours_ahead=24)


class FareHistorySerializer(serializers.ModelSerializer):
    """Serializer for fare history data."""
    
    flight_no = serializers.CharField(source='flight.flight_no', read_only=True)
    
    class Meta:
        model = FareHistory
        fields = [
            'id', 'flight_no', 'calculated_fare', 'seats_remaining',
            'demand_level', 'time_to_departure', 'seat_factor',
            'time_factor', 'demand_factor', 'recorded_at'
        ]


class FlightSearchSerializer(serializers.Serializer):
    """Serializer for flight search parameters."""
    
    origin = serializers.CharField(
        max_length=3, 
        help_text="Origin airport IATA code"
    )
    destination = serializers.CharField(
        max_length=3, 
        help_text="Destination airport IATA code"
    )
    date = serializers.DateField(
        help_text="Departure date (YYYY-MM-DD)"
    )
    sort_by = serializers.ChoiceField(
        choices=[
            ('departure_time', 'Departure Time'),
            ('arrival_time', 'Arrival Time'),
            ('base_fare', 'Base Fare'),
            ('dynamic_fare', 'Current Price'),
            ('duration', 'Duration'),
        ],
        default='departure_time',
        required=False,
        help_text="Sort flights by specified field"
    )
    sort_order = serializers.ChoiceField(
        choices=[('asc', 'Ascending'), ('desc', 'Descending')],
        default='asc',
        required=False,
        help_text="Sort order"
    )
    max_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Maximum price filter"
    )
    airline = serializers.CharField(
        max_length=3,
        required=False,
        help_text="Filter by airline code"
    )
    
    def validate(self, data):
        """Validate search parameters."""
        if data['origin'] == data['destination']:
            raise serializers.ValidationError(
                "Origin and destination cannot be the same."
            )
        
        # Validate airport codes exist
        from .models import Airport
        
        try:
            Airport.objects.get(iata_code=data['origin'])
        except Airport.DoesNotExist:
            raise serializers.ValidationError(
                f"Origin airport '{data['origin']}' not found."
            )
        
        try:
            Airport.objects.get(iata_code=data['destination'])
        except Airport.DoesNotExist:
            raise serializers.ValidationError(
                f"Destination airport '{data['destination']}' not found."
            )
        
        return data


class FlightCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new flights (admin use)."""
    
    class Meta:
        model = Flight
        fields = [
            'flight_no', 'airline', 'origin', 'destination',
            'departure_time', 'arrival_time', 'base_fare',
            'total_seats', 'aircraft_type'
        ]
    
    def validate(self, data):
        """Validate flight creation data."""
        if data['departure_time'] >= data['arrival_time']:
            raise serializers.ValidationError(
                "Departure time must be before arrival time."
            )
        
        if data['origin'] == data['destination']:
            raise serializers.ValidationError(
                "Origin and destination cannot be the same."
            )
        
        return data
    
    def create(self, validated_data):
        """Create flight with initial seat availability."""
        flight = Flight.objects.create(**validated_data)
        flight.seats_available = flight.total_seats
        flight.save()
        return flight