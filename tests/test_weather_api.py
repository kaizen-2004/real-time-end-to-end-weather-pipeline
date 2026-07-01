import pytest
import os
from unittest.mock import patch, MagicMock
from include.extract.weather_api import WeatherAPIClient
from include.extract.rate_limiter import RateLimiter


class TestRateLimiter:
    def test_init(self):
        limiter = RateLimiter(max_calls=60, per_seconds=60)
        assert limiter.max_calls == 60
        assert limiter.per_seconds == 60

    def test_daily_budget(self):
        limiter = RateLimiter()
        budget = limiter.daily_budget_remaining()
        assert budget == 1000


class TestWeatherAPIClient:
    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"})
    def test_init(self):
        client = WeatherAPIClient()
        assert client.api_key == "test_key"

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"})
    @patch("include.extract.weather_api.requests.Session")
    def test_get_current(self, mock_session):
        mock_response = MagicMock()
        mock_response.json.return_value = {"main": {"temp": 20.0}}
        mock_response.raise_for_status = MagicMock()
        mock_session.return_value.get.return_value = mock_response

        client = WeatherAPIClient()
        result = client.get_current(41.89, 12.51)

        assert result == {"main": {"temp": 20.0}}
