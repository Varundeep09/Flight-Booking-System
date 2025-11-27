#!/usr/bin/env python3
"""
Flight Search API Runner
"""

import subprocess
import sys

def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def setup_database():
    from models import create_tables, seed_data
    create_tables()
    seed_data()
    print("✅ Database setup complete")

def run_server():
    import uvicorn
    from main import app
    
    print("🚀 Starting Flight Search API...")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("🔍 Test Search: http://localhost:8000/flights/search?origin=DEL&destination=BOM&date=2024-01-20")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    print("🛫 Flight Search API")
    print("=" * 30)
    
    try:
        print("📦 Installing requirements...")
        install_requirements()
        
        print("🗄️ Setting up database...")
        setup_database()
        
        print("🌐 Starting server...")
        run_server()
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")