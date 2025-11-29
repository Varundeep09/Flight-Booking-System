import requests

def test_api():
    base_url = "http://localhost:8000"
    
    print("Testing API...")
    
    # Test get all flights
    try:
        response = requests.get(f"{base_url}/flights")
        if response.status_code == 200:
            print("✓ Get flights works")
        else:
            print("✗ Get flights failed")
    except:
        print("✗ Server not running")
        return
    
    # Test search
    try:
        response = requests.get(f"{base_url}/search?origin=DEL&destination=BOM&date=2024-01-20")
        if response.status_code == 200:
            results = response.json()
            print(f"✓ Search found {len(results)} flights")
        else:
            print("✗ Search failed")
    except:
        print("✗ Search error")

if __name__ == "__main__":
    test_api()