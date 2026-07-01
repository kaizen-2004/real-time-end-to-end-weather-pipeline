import json
import logging
import os
import psycopg2

logger = logging.getLogger(__name__)


class PostgresLoader:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.environ.get("PGHOST", "postgres"),
            port=os.environ.get("PGPORT", "5432"),
            database=os.environ.get("PGDATABASE", "weather_staging"),
            user=os.environ.get("PGUSER", "weather_user"),
            password=os.environ.get("PGPASSWORD", "weather_pass"),
        )
        self.conn.autocommit = True

    def load_current(self, city: dict, data: dict) -> int:
        sql = """
            INSERT INTO raw.weather_current 
                (city_id, city_name, country_code, latitude, longitude, payload)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        cursor = self.conn.cursor()
        cursor.execute(
            sql,
            (
                city["city_id"],
                city["name"],
                city["country"],
                city["lat"],
                city["lon"],
                json.dumps(data),
            ),
        )
        row_id = cursor.fetchone()[0]
        cursor.close()
        return row_id

    def load_forecast(self, city: dict, data: dict) -> int:
        sql = """
            INSERT INTO raw.weather_forecast
                (city_id, city_name, latitude, longitude, payload)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """
        cursor = self.conn.cursor()
        cursor.execute(
            sql,
            (
                city["city_id"],
                city["name"],
                city["lat"],
                city["lon"],
                json.dumps(data),
            ),
        )
        row_id = cursor.fetchone()[0]
        cursor.close()
        return row_id

    def close(self):
        if self.conn:
            self.conn.close()
