# Philippine Weather Pipeline

End-to-end ELT data pipeline that tracks real-time weather across 5 Philippine cities using Apache Airflow, PostgreSQL, dbt, and Snowflake.

[Live Dashboard](https://kaizen-2004.github.io/real-time-end-to-end-weather-pipeline/) | [Snowflake Query](https://app.snowflake.com) | [Author](https://steve-villa-devportfolio.netlify.app/)

---

## Overview

This project demonstrates a production-grade data pipeline following the ELT pattern (Extract, Load, Transform). Weather data is extracted from the OpenWeatherMap API every 30 minutes, staged in PostgreSQL, transformed with dbt, and loaded into Snowflake as a star schema optimized for analytics.

### Key Features

- **Automated ingestion** — Apache Airflow orchestrates the pipeline on a 30-minute schedule
- **ELT pattern** — Raw data lands first, transformations happen in the warehouse
- **Star schema** — Dimensional modeling with dim_cities, dim_dates, and fact tables
- **Rate limiting** — Respects OpenWeatherMap's 1,000 calls/day free tier
- **Containerized** — Full stack runs locally with Docker Compose
- **Live dashboard** — Interactive geospatial visualization with Chart.js and Leaflet

---

## Architecture

```
OpenWeatherMap API
        |
        v
   [Airflow DAG]  --- extracts every 30 min
        |
        v
  PostgreSQL (raw)  --- JSONB landing zone
        |
        v
    dbt models  --- staging -> intermediate -> marts
        |
        v
  Snowflake (marts)  --- star schema for analytics
```

### Data Flow

1. **Extract** — `weather_api.py` calls `/weather` and `/forecast` for 5 cities
2. **Load** — Raw JSON lands in PostgreSQL `raw` schema as JSONB
3. **Transform** — dbt flattens JSON, aggregates data, builds star schema
4. **Serve** — Snowflake tables power the dashboard and ad-hoc queries

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Orchestration | Apache Airflow 2.9 | Schedule and monitor pipeline |
| Staging | PostgreSQL 16 | Raw data landing zone |
| Transformation | dbt 1.7 | SQL-based ELT models |
| Warehouse | Snowflake | Analytics-ready star schema |
| Containerization | Docker Compose | Reproducible local environment |
| API | OpenWeatherMap | Weather data source |
| Dashboard | Chart.js + Leaflet | Interactive visualization |

---

## Cities Tracked

| City | Coordinates |
|------|-------------|
| Manila | 14.5995°N, 120.9842°E |
| Cebu City | 10.3157°N, 123.8854°E |
| Davao City | 7.1907°N, 125.4553°E |
| Makati | 14.5547°N, 121.0500°E |
| Quezon City | 14.6760°N, 121.0437°E |

---

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Snowflake account ([free trial](https://signup.snowflake.com/))
- OpenWeatherMap API key ([free tier](https://openweathermap.org/api))

### Installation

```bash
# Clone the repository
git clone https://github.com/kaizen-2004/real-time-end-to-end-weather-pipeline.git
cd real-time-end-to-end-weather-pipeline

# Configure environment variables
cp .env.example .env
# Edit .env with your Snowflake and OpenWeatherMap credentials

# Start all services
docker compose up -d

# Initialize Snowflake schemas
docker compose exec airflow-scheduler python /opt/airflow/scripts/seed_snowflake.py
```

### Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Airflow UI | http://localhost:8080 | admin / admin |
| PostgreSQL | localhost:5433 | weather_user / weather_pass |
| Snowflake | https://app.snowflake.com | Your account |

---

## Usage

### Trigger Pipeline Manually

```bash
# Trigger a DAG run
docker compose exec airflow-scheduler airflow dags trigger weather_pipeline

# Check run status
docker compose exec airflow-scheduler airflow dags list-runs -d weather_pipeline --limit 5
```

### Run dbt Models

```bash
# Run all models
docker compose run --rm dbt-runner run

# Run specific layers
docker compose run --rm dbt-runner run --select staging
docker compose run --rm dbt-runner run --select marts

# Run tests
docker compose run --rm dbt-runner test
```

### Query Snowflake

```sql
-- Current weather by city
SELECT 
    c.city_name,
    r.temperature_f,
    r.humidity_pct,
    r.weather_condition
FROM RAW_MARTS.FCT_WEATHER_READINGS r
JOIN RAW_MARTS.DIM_CITIES c ON r.city_id = c.city_id
ORDER BY r.reading_timestamp DESC;

-- Daily forecast summary
SELECT 
    c.city_name,
    d.avg_temperature_k,
    d.min_temperature_k,
    d.max_temperature_k,
    d.dominant_condition
FROM RAW_MARTS.FCT_DAILY_WEATHER d
JOIN RAW_MARTS.DIM_CITIES c ON d.city_id = c.city_id
ORDER BY c.city_name, d.date_key;
```

---

## Project Structure

```
weather-pipeline/
├── dags/                    # Airflow DAG definitions
├── include/                 # Shared Python modules
│   ├── extract/             # API client, rate limiter
│   └── load/                # PostgreSQL loader
├── dbt/                     # dbt project
│   ├── models/
│   │   ├── staging/         # Flatten raw JSON
│   │   ├── intermediate/    # Aggregations
│   │   └── marts/           # Star schema
│   └── seeds/               # Reference data (cities)
├── sql/                     # Database init scripts
│   ├── postgres/
│   └── snowflake/
├── scripts/                 # Setup utilities
├── tests/                   # Unit tests
├── dashboard/               # Interactive dashboard
├── docker-compose.yml       # Service orchestration
└── .env.example             # Environment template
```

---

## Data Schema

### Snowflake Star Schema

```
dim_cities                dim_dates
├── city_id (PK)          ├── date_key (PK)
├── city_name             ├── full_date
├── country_code          ├── year, month, day
├── latitude              ├── day_of_week
├── longitude             └── is_weekend
└── timezone_offset

fct_weather_readings      fct_daily_weather
├── reading_id (PK)       ├── city_id (FK)
├── city_id (FK)          ├── date_key (FK)
├── date_key (FK)         ├── avg_temperature_k
├── temperature_k         ├── min_temperature_k
├── temperature_f         ├── max_temperature_k
├── humidity_pct          ├── avg_humidity_pct
├── weather_condition     └── dominant_condition
└── reading_timestamp
```

---

## Rate Limiting

| Metric | Value |
|--------|-------|
| OpenWeatherMap free tier | 1,000 calls/day |
| Pipeline per run | 10 calls (5 cities x 2 endpoints) |
| Daily usage (30-min intervals) | ~480 calls (48% of budget) |
| Rate limiter | Max 60 calls/minute with backoff |

---

## Development

### Run Tests

```bash
# Python tests
docker compose exec airflow-scheduler python -m pytest /opt/airflow/tests/

# dbt tests
docker compose run --rm dbt-runner test
```

### View Logs

```bash
# Airflow scheduler
docker compose logs -f airflow-scheduler

# Airflow webserver
docker compose logs -f airflow-webserver
```

### Stop Services

```bash
docker compose down

# Remove volumes (fresh start)
docker compose down -v
```

---

## Author

**Steve A. Villa** — BS Computer Engineering

- [Portfolio](https://steve-villa-devportfolio.netlify.app/)
- [GitHub](https://github.com/kaizen-2004)

---

## License

This project is open source and available for portfolio demonstration purposes.
