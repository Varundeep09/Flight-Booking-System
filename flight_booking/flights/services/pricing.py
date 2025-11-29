import random

def calculate_price(base_price, seats_left, total_seats):
    # Simple pricing logic
    occupancy = (total_seats - seats_left) / total_seats
    
    if occupancy > 0.8:
        multiplier = 1.5
    elif occupancy > 0.5:
        multiplier = 1.2
    else:
        multiplier = 1.0
    
    # Add some randomness
    demand_factor = random.uniform(0.9, 1.3)
    
    final_price = base_price * multiplier * demand_factor
    return round(final_price, 2)

def get_dynamic_price(flight):
    return calculate_price(
        float(flight.price),
        flight.seats,
        180  # assume 180 total seats
    )