import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("Testing Flight Search API...")
    
    try:
        # Test 1: Get all flights
        print("\n1. Testing GET /flights")
        response = requests.get(f"{BASE_URL}/flights")
        if response.status_code == 200:
            flights = response.json()
            print(f"✓ Found {len(flights)} flights")
        else:
            print(f"✗ Error: {response.status_code}")
        
        # Test 2: Search flights
        print("\n2. Testing flight search")
        params = {
            "origin": "DEL",
            "destination": "BOM", 
            "date": "2024-01-20"
        }
        response = requests.get(f"{BASE_URL}/search", params=params)
        if response.status_code == 200:
            results = response.json()
            print(f"✓ Search returned {len(results)} flights")
            if results:
                print(f"  First result: {results[0]['flight_no']} - ₹{results[0]['price']}")
        else:
            print(f"✗ Search failed: {response.status_code}")
        
        # Test 3: Get specific flight
        print("\n3. Testing GET /flights/1")
        response = requests.get(f"{BASE_URL}/flights/1")
        if response.status_code == 200:
            flight = response.json()
            print(f"✓ Flight details: {flight['flight_no']}")
        else:
            print(f"✗ Flight not found: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Make sure server is running on port 8000")

if __name__ == "__main__":
    test_endpoints()