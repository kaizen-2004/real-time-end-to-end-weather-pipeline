import requests
import logging
import os
import time
from include.extract.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class WeatherAPIClient:
    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self):
        self.api_key = os.environ.get("OPENWEATHER_API_KEY", "")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.rate_limiter = RateLimiter(max_calls=60, per_seconds=60)

    def _get(self, endpoint: str, params: dict) -> dict | None:
        self.rate_limiter.wait_if_needed()

        params["appid"] = self.api_key
        params["units"] = "metric"

        try:
            resp = self.session.get(
                f"{self.BASE_URL}/{endpoint}",
                params=params,
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 429:
                logger.warning("Rate limited, backing off for 5 minutes")
                time.sleep(300)
                return self._get(endpoint, params)
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def get_current(self, lat: float, lon: float) -> dict | None:
        return self._get("weather", {"lat": lat, "lon": lon})

    def get_forecast(self, lat: float, lon: float) -> dict | None:
        return self._get("forecast", {"lat": lat, "lon": lon})
