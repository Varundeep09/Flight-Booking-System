#!/usr/bin/env python3
"""
Milestone 1 Runner - Flight Search API
Run this to start the complete Milestone 1 implementation
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "milestone1_requirements.txt"])

def setup_database():
    """Initialize database with sample data"""
    from milestone1_database import create_tables, populate_sample_data
    create_tables()
    populate_sample_data()
    print("✅ Database setup complete with sample data")

def run_api():
    """Start the FastAPI server"""
    import uvicorn
    from milestone1_api import app
    
    print("🚀 Starting Flight Search API...")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("🔍 Test Search: http://localhost:8000/flights/search?origin=DEL&destination=BOM&date=2024-01-15")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    print("🛫 Flight Booking Simulator - Milestone 1")
    print("=" * 50)
    
    try:
        print("📦 Installing requirements...")
        install_requirements()
        
        print("🗄️ Setting up database...")
        setup_database()
        
        print("🌐 Starting API server...")
        run_api()
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")