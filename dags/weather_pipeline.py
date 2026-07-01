import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

logger = logging.getLogger(__name__)

sys.path.insert(0, "/opt/airflow")
CONFIG_DIR = Path("/opt/airflow/config")


def load_cities() -> list[dict]:
    with open(CONFIG_DIR / "cities.json") as f:
        return json.load(f)["cities"]


def extract_current_weather(**context):
    from include.extract.weather_api import WeatherAPIClient
    from include.load.postgres_loader import PostgresLoader

    client = WeatherAPIClient()
    loader = PostgresLoader()
    cities = load_cities()

    for city in cities:
        try:
            data = client.get_current(city["lat"], city["lon"])
            if data:
                loader.load_current(city, data)
                logger.info(f"Loaded current weather for {city['name']}")
        except Exception as e:
            logger.error(f"Failed for {city['name']}: {e}")
            raise

    loader.close()


def extract_forecast(**context):
    from include.extract.weather_api import WeatherAPIClient
    from include.load.postgres_loader import PostgresLoader

    client = WeatherAPIClient()
    loader = PostgresLoader()
    cities = load_cities()

    for city in cities:
        try:
            data = client.get_forecast(city["lat"], city["lon"])
            if data:
                loader.load_forecast(city, data)
                logger.info(f"Loaded forecast for {city['name']}")
        except Exception as e:
            logger.error(f"Failed for {city['name']}: {e}")
            raise

    loader.close()


default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=10),
    "email_on_failure": False,
    "email_on_retry": False,
}

with DAG(
    dag_id="weather_pipeline",
    default_args=default_args,
    description="ELT: OpenWeatherMap -> PostgreSQL -> Snowflake",
    schedule_interval="*/30 * * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["weather", "portfolio", "elt"],
) as dag:

    start = EmptyOperator(task_id="start")

    extract_current = PythonOperator(
        task_id="extract_current_weather",
        python_callable=extract_current_weather,
    )

    extract_forecast = PythonOperator(
        task_id="extract_forecast",
        python_callable=extract_forecast,
    )

    end = EmptyOperator(task_id="end")

    start >> [extract_current, extract_forecast] >> end
