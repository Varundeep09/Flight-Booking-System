import subprocess
import sys

def install_deps():
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def setup_db():
    import models
    models.add_flights()
    print("Database ready")

def start_server():
    import uvicorn
    from app import app
    print("Starting server...")
    uvicorn.run(app, port=8000)

if __name__ == "__main__":
    print("Flight API Setup")
    install_deps()
    setup_db()
    start_server()