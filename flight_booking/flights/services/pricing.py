"""
Dynamic pricing engine for flight fares.
"""
from datetime import datetime
import random
from decimal import Decimal
from django.utils import timezone
from ..models import FareHistory


class PricingEngine:
    """
    Dynamic pricing engine that calculates flight fares based on:
    1. Seat availability (occupancy rate)
    2. Time to departure
    3. Simulated demand level
    """
    
    @staticmethod
    def calculate_seat_factor(seats_available, total_seats):
        """
        Calculate pricing factor based on seat availability.
        
        Args:
            seats_available (int): Number of available seats
            total_seats (int): Total seats in aircraft
            
        Returns:
            Decimal: Pricing factor based on occupancy
        """
        if total_seats == 0:
            return Decimal('1.0')
            
        occupancy_rate = (total_seats - seats_available) / total_seats
        
        if occupancy_rate >= 0.8:  # Less than 20% seats left
            return Decimal('1.5')  # 50% increase
        elif occupancy_rate >= 0.5:  # 50-80% occupied
            return Decimal('1.2')  # 20% increase
        elif occupancy_rate >= 0.3:  # 30-50% occupied
            return Decimal('1.1')  # 10% increase
        else:  # Low occupancy
            return Decimal('0.95')  # 5% discount
    
    @staticmethod
    def calculate_time_factor(departure_time):
        """
        Calculate pricing factor based on time until departure.
        
        Args:
            departure_time (datetime): Flight departure time
            
        Returns:
            Decimal: Pricing factor based on time remaining
        """
        now = timezone.now()
        
        # Handle timezone-naive datetime
        if departure_time.tzinfo is None:
            departure_time = timezone.make_aware(departure_time)
        
        time_diff = departure_time - now
        hours_left = time_diff.total_seconds() / 3600
        
        if hours_left < 0:  # Flight has already departed
            return Decimal('0.0')
        elif hours_left < 24:  # Less than 24 hours
            return Decimal('1.4')  # 40% increase
        elif hours_left < 72:  # 1-3 days
            return Decimal('1.2')  # 20% increase
        elif hours_left < 168:  # 3-7 days
            return Decimal('1.1')  # 10% increase
        else:  # More than 7 days
            return Decimal('1.0')  # No change
    
    @staticmethod
    def calculate_demand_factor(flight_id=None):
        """
        Simulate demand factor based on various conditions.
        
        Args:
            flight_id (int, optional): Flight ID for route-specific demand
            
        Returns:
            tuple: (demand_factor, demand_level)
        """
        # Demand levels with their corresponding factors
        demand_levels = {
            'LOW': Decimal('1.0'),
            'MEDIUM': Decimal('1.15'),
            'HIGH': Decimal('1.3')
        }
        
        # Simulate demand based on various factors
        # In a real system, this could be based on:
        # - Historical booking data
        # - Search volume
        # - Route popularity
        # - Seasonal trends
        # - Events in destination city
        
        # For simulation, use weighted random selection
        demand_weights = [0.3, 0.5, 0.2]  # 30% low, 50% medium, 20% high
        current_demand = random.choices(
            list(demand_levels.keys()), 
            weights=demand_weights
        )[0]
        
        return demand_levels[current_demand], current_demand
    
    @classmethod
    def calculate_dynamic_fare(cls, flight, save_history=True):
        """
        Calculate the final dynamic fare for a flight.
        
        Args:
            flight (Flight): Flight instance
            save_history (bool): Whether to save fare calculation to history
            
        Returns:
            dict: Comprehensive pricing details
        """
        base_fare = flight.base_fare
        
        # Calculate individual factors
        seat_factor = cls.calculate_seat_factor(
            flight.seats_available, 
            flight.total_seats
        )
        
        time_factor = cls.calculate_time_factor(flight.departure_time)
        demand_factor, demand_level = cls.calculate_demand_factor(flight.id)
        
        # Calculate final fare
        dynamic_fare = base_fare * seat_factor * time_factor * demand_factor
        
        # Round to nearest rupee
        final_fare = round(dynamic_fare, 2)
        
        # Calculate time to departure in hours
        now = timezone.now()
        departure_time = flight.departure_time
        if departure_time.tzinfo is None:
            departure_time = timezone.make_aware(departure_time)
        
        time_to_departure = max(0, (departure_time - now).total_seconds() / 3600)
        
        # Prepare pricing details
        pricing_details = {
            'base_fare': float(base_fare),
            'dynamic_fare': float(final_fare),
            'seat_factor': float(seat_factor),
            'time_factor': float(time_factor),
            'demand_factor': float(demand_factor),
            'demand_level': demand_level,
            'occupancy_rate': flight.occupancy_rate,
            'seats_remaining': flight.seats_available,
            'time_to_departure_hours': int(time_to_departure),
            'price_increase_percentage': round(
                ((final_fare - base_fare) / base_fare) * 100, 1
            )
        }
        
        # Save to fare history for analytics
        if save_history:
            try:
                FareHistory.objects.create(
                    flight=flight,
                    calculated_fare=final_fare,
                    seats_remaining=flight.seats_available,
                    demand_level=demand_level,
                    time_to_departure=int(time_to_departure),
                    seat_factor=seat_factor,
                    time_factor=time_factor,
                    demand_factor=demand_factor
                )
            except Exception as e:
                # Log error but don't fail the pricing calculation
                print(f"Error saving fare history: {e}")
        
        return pricing_details
    
    @classmethod
    def get_fare_trends(cls, flight, days=7):
        """
        Get fare trend data for a flight over specified days.
        
        Args:
            flight (Flight): Flight instance
            days (int): Number of days to look back
            
        Returns:
            list: Fare history data
        """
        from django.utils import timezone
        from datetime import timedelta
        
        start_date = timezone.now() - timedelta(days=days)
        
        return FareHistory.objects.filter(
            flight=flight,
            recorded_at__gte=start_date
        ).order_by('recorded_at').values(
            'calculated_fare',
            'demand_level',
            'seats_remaining',
            'recorded_at'
        )
    
    @classmethod
    def simulate_price_changes(cls, flight, hours_ahead=24):
        """
        Simulate how prices might change over time.
        
        Args:
            flight (Flight): Flight instance
            hours_ahead (int): Hours to simulate ahead
            
        Returns:
            list: Projected price changes
        """
        projections = []
        current_seats = flight.seats_available
        
        for hour in range(0, hours_ahead + 1, 6):  # Every 6 hours
            # Simulate gradual seat reduction
            simulated_seats = max(0, current_seats - (hour // 12))
            
            # Create temporary flight object for calculation
            temp_departure = flight.departure_time
            if temp_departure.tzinfo is None:
                temp_departure = timezone.make_aware(temp_departure)
            
            # Simulate time progression
            simulated_departure = temp_departure - timezone.timedelta(hours=hour)
            
            # Calculate factors
            seat_factor = cls.calculate_seat_factor(simulated_seats, flight.total_seats)
            time_factor = cls.calculate_time_factor(simulated_departure)
            demand_factor, demand_level = cls.calculate_demand_factor()
            
            projected_fare = flight.base_fare * seat_factor * time_factor * demand_factor
            
            projections.append({
                'hours_from_now': hour,
                'projected_fare': round(projected_fare, 2),
                'seats_remaining': simulated_seats,
                'demand_level': demand_level
            })
        
        return projections