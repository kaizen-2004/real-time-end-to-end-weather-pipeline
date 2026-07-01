# Weather Pipeline — Real-Time ELT with Airflow, dbt, PostgreSQL & Snowflake

A production-grade, near real-time data pipeline that ingests weather data from OpenWeatherMap, stages it in PostgreSQL, transforms with dbt, and loads into Snowflake — all orchestrated with Apache Airflow on Docker.

## Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  OpenWeather │───→│  PostgreSQL  │───→│     dbt      │───→│   Snowflake  │
│     API      │    │   (staging)  │    │  (transform) │    │  (warehouse) │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
   Every 30 min       JSONB landing      Star schema          Analytics-ready
                      zone               ELT models           data warehouse
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Data Source | OpenWeatherMap API (free tier: 1000 calls/day) |
| Orchestration | Apache Airflow 2.9 |
| Staging DB | PostgreSQL 16 (Docker) |
| Transformation | dbt 1.7 (Snowflake adapter) |
| Warehouse | Snowflake (free trial) |
| Containerization | Docker Compose |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Snowflake account (free trial works)
- OpenWeatherMap API key (free tier)

### Setup

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env with your API keys

# 2. Start the stack
docker compose up -d

# 3. Initialize Snowflake schemas
docker compose exec airflow-scheduler python /opt/airflow/scripts/seed_snowflake.py
```

### Pipeline Dashboard
- **Airflow UI**: http://localhost:8080 (admin / admin)
- **PostgreSQL**: localhost:5433 (weather_user / weather_pass)
- **Snowflake**: https://app.snowflake.com

## How It Works

### 1. Data Extraction (every 30 minutes)
The Airflow DAG triggers `weather_api.py` which calls OpenWeatherMap's
`/weather` and `/forecast` endpoints for 5 Philippine cities (Manila, Cebu City,
Davao City, Makati, Quezon City). Rate limiting ensures we stay within the
1000 calls/day free tier.

### 2. Staging (PostgreSQL)
Raw JSON payloads land in PostgreSQL's `raw` schema as JSONB columns.

### 3. Transformation (dbt)
dbt runs three model layers:
- **Staging**: Flatten JSONB into typed columns
- **Intermediate**: Aggregate hourly/daily summaries
- **Marts**: Star schema with dimensions and facts for analytics

### 4. Warehouse (Snowflake)
The final Snowflake schema provides:
- `dim_cities` — City lookup with coordinates
- `dim_dates` — Date dimension for time-based analysis
- `fct_weather_readings` — Individual weather observations
- `fct_daily_weather` — Daily weather summaries per city

## Project Structure

```
weather-pipeline/
├── dags/                    # Airflow DAGs
├── include/                 # Shared Python code
│   ├── extract/             # API client + rate limiter
│   └── load/                # PostgreSQL loader
├── dbt/                     # dbt project
│   ├── models/              # SQL models
│   │   ├── staging/         # Flatten raw data
│   │   ├── intermediate/    # Aggregations
│   │   └── marts/           # Star schema
│   └── seeds/               # Reference data
├── sql/                     # Database init scripts
│   ├── postgres/            # Staging tables
│   └── snowflake/           # Warehouse tables
├── config/                  # City configuration
├── scripts/                 # Setup utilities
├── tests/                   # Unit tests
└── docs/                    # Documentation
```

## Running Locally

```bash
# Start full stack
docker compose up -d

# Run pipeline manually
docker compose exec airflow-scheduler airflow dags trigger weather_pipeline

# Run dbt models
docker compose run --rm dbt-runner run

# Run dbt tests
docker compose run --rm dbt-runner test

# View logs
docker compose logs -f airflow-scheduler
```

## Sample Queries

```sql
-- Set up context
USE DATABASE WEATHER_PIPELINE;
USE WAREHOUSE WEATHER_WH;

-- Current weather by city
SELECT 
    c.city_name,
    r.temperature_f,
    r.humidity_pct,
    r.weather_condition,
    r.reading_timestamp
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

-- All cities tracked
SELECT * FROM RAW_MARTS.DIM_CITIES;

-- Date range available
SELECT MIN(full_date) as start_date, MAX(full_date) as end_date 
FROM RAW_MARTS.DIM_DATES;
```

## Rate Limiting

- **OpenWeatherMap free tier**: 1,000 API calls/day
- **Pipeline per run**: 5 cities × 2 endpoints = 10 calls
- **Daily at 30-min intervals**: 48 runs × 10 = 480 calls (48% of budget)
- **Built-in rate limiter**: Max 60 calls/minute with automatic backoff

## Portfolio Highlights

- ✅ **ELT Pattern**: Extract → Load → Transform (industry standard)
- ✅ **Modern Stack**: Airflow + dbt + Snowflake (most requested DE skills)
- ✅ **Containerized**: Docker Compose for reproducible local dev
- ✅ **Star Schema**: Proper dimensional modeling in Snowflake
- ✅ **Data Quality**: dbt tests ensure data integrity
- ✅ **Production Patterns**: Rate limiting, retries, error handling
- ✅ **5 Cities Tracked**: Manila, Cebu City, Davao City, Makati, Quezon City
