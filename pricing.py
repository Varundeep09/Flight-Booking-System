from datetime import datetime
import random

def calculate_dynamic_price(base_fare, seats_available, total_seats, departure_time):
    # Calculate seat availability factor
    occupancy = (total_seats - seats_available) / total_seats
    
    if occupancy > 0.8:
        seat_factor = 0.5
    elif occupancy > 0.5:
        seat_factor = 0.2
    else:
        seat_factor = 0.0
    
    # Calculate time factor
    dep_time = datetime.fromisoformat(departure_time)
    hours_left = (dep_time - datetime.now()).total_seconds() / 3600
    
    if hours_left < 24:
        time_factor = 0.4
    elif hours_left < 72:
        time_factor = 0.2
    elif hours_left < 168:
        time_factor = 0.1
    else:
        time_factor = 0.0
    
    # Simulate demand
    demand_level = random.choice(['low', 'medium', 'high'])
    if demand_level == 'high':
        demand_factor = 0.3
    elif demand_level == 'medium':
        demand_factor = 0.15
    else:
        demand_factor = 0.0
    
    # Calculate final price
    total_factor = 1 + seat_factor + time_factor + demand_factor
    final_price = base_fare * total_factor
    
    return round(final_price, 2)

def get_price_breakdown(base_fare, seats_available, total_seats, departure_time):
    occupancy = (total_seats - seats_available) / total_seats
    dep_time = datetime.fromisoformat(departure_time)
    hours_left = (dep_time - datetime.now()).total_seconds() / 3600
    
    if occupancy > 0.8:
        seat_factor = 0.5
    elif occupancy > 0.5:
        seat_factor = 0.2
    else:
        seat_factor = 0.0
    
    if hours_left < 24:
        time_factor = 0.4
    elif hours_left < 72:
        time_factor = 0.2
    elif hours_left < 168:
        time_factor = 0.1
    else:
        time_factor = 0.0
    
    demand_level = random.choice(['low', 'medium', 'high'])
    if demand_level == 'high':
        demand_factor = 0.3
    elif demand_level == 'medium':
        demand_factor = 0.15
    else:
        demand_factor = 0.0
    
    final_price = base_fare * (1 + seat_factor + time_factor + demand_factor)
    
    return {
        'base_fare': base_fare,
        'dynamic_price': round(final_price, 2),
        'seat_factor': seat_factor,
        'time_factor': time_factor,
        'demand_factor': demand_factor,
        'demand_level': demand_level,
        'occupancy': round(occupancy * 100, 1)
    }