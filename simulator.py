import asyncio
import database
import random
from datetime import datetime

async def simulate_market_step():
    """Simulate demand and availability changes"""
    print(f"Running simulation at {datetime.now().strftime('%H:%M:%S')}")
    database.simulate_demand_change()

async def scheduler_loop(interval):
    """Run simulation at regular intervals"""
    while True:
        await simulate_market_step()
        await asyncio.sleep(interval)

if __name__ == "__main__":
    print("Starting demand simulator...")
    print("Simulating every 60 seconds")
    asyncio.run(scheduler_loop(60))