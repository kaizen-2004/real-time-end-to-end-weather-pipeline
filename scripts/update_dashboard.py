"""Publish a weather snapshot without rewriting the dashboard's static files."""

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

import requests

API_URL = "https://api.openweathermap.org/data/2.5/weather"
SNAPSHOT_PATH = Path(__file__).resolve().parents[1] / "dashboard" / "weather.json"

CITIES = (
    ("Manila", 14.5995, 120.9842),
    ("Cebu City", 10.3157, 123.8854),
    ("Davao City", 7.1907, 125.4553),
    ("Makati", 14.5547, 121.0500),
    ("Quezon City", 14.6760, 121.0437),
)


class Reading(TypedDict):
    city: str
    lat: float
    lon: float
    temp: int | None
    feels_like: int | None
    humidity: int | None
    wind: int | None
    description: str
    observed_at: str | None


def fetch_weather(api_key: str) -> list[Reading]:
    readings: list[Reading] = []
    with requests.Session() as session:
        for name, lat, lon in CITIES:
            reading: Reading = {
                "city": name, "lat": lat, "lon": lon, "temp": None,
                "feels_like": None, "humidity": None, "wind": None,
                "description": "Data unavailable", "observed_at": None,
            }
            try:
                response = session.get(API_URL, params={
                    "lat": lat, "lon": lon, "appid": api_key, "units": "metric"
                }, timeout=10)
                response.raise_for_status()
                data = response.json()
                temp = float(data["main"]["temp"])
                feels_like = float(data["main"]["feels_like"])
                humidity = float(data["main"]["humidity"])
                wind = float(data["wind"]["speed"]) * 3.6
                if not all(map(math.isfinite, (temp, feels_like, humidity, wind))):
                    raise ValueError("Non-finite weather reading")
                if not 0 <= humidity <= 100 or wind < 0:
                    raise ValueError("Weather reading out of range")
                observed = datetime.fromtimestamp(data["dt"], tz=timezone.utc).isoformat()
                description = data["weather"][0]["description"].title()
            except (requests.RequestException, ValueError, KeyError, TypeError, IndexError, AttributeError, OverflowError, OSError) as error:
                # Request exception strings can include the API key in the URL.
                print(f"Could not fetch {name}: {type(error).__name__}")
            else:
                reading.update(temp=round(temp), feels_like=round(feels_like),
                               humidity=round(humidity), wind=round(wind),
                               description=description, observed_at=observed)
            readings.append(reading)
    return readings


def write_snapshot(readings: list[Reading], path: Path = SNAPSHOT_PATH) -> int:
    count = sum(reading["observed_at"] is not None for reading in readings)
    if not count:
        raise SystemExit("No city readings were retrieved; keeping the previous snapshot.")
    snapshot = {"published_at": datetime.now(timezone.utc).isoformat(), "cities": readings}
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(snapshot, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)
    return count


def main() -> None:
    api_key = os.environ.get("OPENWEATHER_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Set OPENWEATHER_API_KEY before updating the dashboard.")
    readings = fetch_weather(api_key)
    count = write_snapshot(readings)
    print(f"Published a snapshot with {count} of {len(readings)} city readings.")


if __name__ == "__main__":
    main()
