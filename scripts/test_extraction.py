#!/usr/bin/env python3
"""Test script to verify extraction and loading works."""
import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from include.extract.weather_api import WeatherAPIClient
from include.load.postgres_loader import PostgresLoader


def test_extraction():
    """Test API extraction for one city."""
    print("Testing API extraction...")
    client = WeatherAPIClient()
    
    # Test current weather (Rome)
    data = client.get_current(41.8919, 12.5113)
    if data:
        print(f"  ✅ Current weather: {data.get('name', 'unknown')} - {data.get('main', {}).get('temp', 'N/A')}°C")
        return True
    else:
        print("  ❌ Failed to get current weather")
        return False


def test_loading():
    """Test loading to PostgreSQL."""
    print("\nTesting PostgreSQL loading...")
    client = WeatherAPIClient()
    loader = PostgresLoader()
    
    city = {"city_id": 3169070, "name": "Rome", "country": "IT", "lat": 41.8919, "lon": 12.5113}
    
    # Load current weather
    data = client.get_current(city["lat"], city["lon"])
    if data:
        row_id = loader.load_current(city, data)
        print(f"  ✅ Loaded current weather for {city['name']} (id: {row_id})")
    else:
        print(f"  ❌ Failed to get current weather for {city['name']}")
        return False
    
    # Load forecast
    data = client.get_forecast(city["lat"], city["lon"])
    if data:
        row_id = loader.load_forecast(city, data)
        print(f"  ✅ Loaded forecast for {city['name']} (id: {row_id})")
    else:
        print(f"  ❌ Failed to get forecast for {city['name']}")
        return False
    
    loader.close()
    return True


def main():
    print("=" * 50)
    print("Weather Pipeline - Sprint 1 Test")
    print("=" * 50)
    
    # Check API key
    api_key = os.environ.get("OPENWEATHER_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        print("\n❌ Please set OPENWEATHER_API_KEY in .env file")
        print("   Edit: projects/weather-pipeline/.env")
        return False
    
    success = True
    success &= test_extraction()
    success &= test_loading()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Sprint 1 test passed!")
    else:
        print("❌ Sprint 1 test failed")
    print("=" * 50)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
