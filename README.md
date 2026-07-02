# Philippine Weather Pipeline

End-to-end ELT data pipeline that tracks real-time weather across 5 Philippine cities using Apache Airflow, PostgreSQL, dbt, and Snowflake. Live dashboard auto-refreshes every 30 minutes with data from OpenWeatherMap API.

[Live Dashboard](https://kaizen-2004.github.io/real-time-end-to-end-weather-pipeline/) | [Author](https://steve-villa-devportfolio.netlify.app/)

---

## Problem Statement

Weather data across the Philippine archipelago varies significantly by region. No automated pipeline existed to collect, transform, and visualize real-time weather data for multiple cities in a structured, analytics-ready format.

## Solution

Built an end-to-end ELT pipeline that:
- Extracts weather data from OpenWeatherMap API for 5 cities
- Stages raw JSON in PostgreSQL
- Transforms with dbt into a star schema
- Loads into Snowflake for analytics
- Visualizes on an interactive geospatial dashboard

---

## Architecture

```
OpenWeatherMap API ──→ GitHub Actions (every 30 min) ──→ Live Dashboard
                          │
                          ▼
                    Airflow DAG ──→ PostgreSQL (raw) ──→ dbt ──→ Snowflake
                                                               │
                                                               ▼
                                                         Star Schema
                                                    (dim_cities, dim_dates,
                                                     fct_weather_readings,
                                                     fct_daily_weather)
```

### Data Flow

| Step | Component | Action | Output |
|------|-----------|--------|--------|
| 1 | OpenWeatherMap API | GET `/weather` for 5 cities | JSON responses |
| 2 | Airflow DAG | Triggers every 30 min | Pipeline execution |
| 3 | PostgreSQL | Stores raw JSONB | `raw.weather_current` |
| 4 | dbt staging | Flattens JSON into typed columns | `staging.stg_weather__current` |
| 5 | dbt marts | Star schema dimensions + facts | `marts.dim_cities`, `fct_weather_readings` |
| 6 | Dashboard | Fetches live API data | Interactive geospatial visualization |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Orchestration | Apache Airflow 2.9 | Schedule and monitor pipeline |
| Staging | PostgreSQL 16 | Raw data landing zone (JSONB) |
| Transformation | dbt 1.7 | SQL-based ELT models |
| Warehouse | Snowflake | Analytics-ready star schema |
| Containerization | Docker Compose | Reproducible local environment |
| API | OpenWeatherMap | Weather data source |
| Dashboard | Chart.js + Leaflet | Interactive geospatial visualization |
| Automation | GitHub Actions | Auto-refresh dashboard every 30 min |

---

## Cities Tracked

| City | Coordinates | Region |
|------|-------------|--------|
| Manila | 14.5995°N, 120.9842°E | Luzon |
| Cebu City | 10.3157°N, 123.8854°E | Visayas |
| Davao City | 7.1907°N, 125.4553°E | Mindanao |
| Makati | 14.5547°N, 121.0500°E | Luzon |
| Quezon City | 14.6760°N, 121.0437°E | Luzon |

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
# Edit .env with your credentials

# Start all services
docker compose up -d

# Initialize Snowflake schemas
docker compose exec airflow-scheduler python /opt/airflow/scripts/seed_snowflake.py
```

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key | `abc123def456` |
| `AIRFLOW_FERNET_KEY` | Airflow encryption key | Generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `SNOWFLAKE_ACCOUNT` | Snowflake account identifier | `abc12345.us-east-1` |
| `SNOWFLAKE_USER` | Snowflake username | `your_username` |
| `SNOWFLAKE_PASSWORD` | Snowflake password | `your_password` |

### Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Airflow UI | http://localhost:8080 | admin / admin |
| PostgreSQL | localhost:5433 | weather_user / weather_pass |
| Snowflake | https://app.snowflake.com | Your account |
| Live Dashboard | https://kaizen-2004.github.io/real-time-end-to-end-weather-pipeline/ | Public |

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

## Dashboard Auto-Refresh

The live dashboard is automatically updated every 30 minutes via GitHub Actions:

1. **GitHub Actions workflow** runs `scripts/update_dashboard.py`
2. Script fetches live data from OpenWeatherMap API
3. Generates new `index.html` with real-time data
4. Commits and pushes to the repository
5. GitHub Pages serves the updated dashboard

### Setting Up Auto-Refresh

1. Add your OpenWeatherMap API key as a GitHub repository secret:
   - Go to Settings → Secrets and variables → Actions
   - Add `OPENWEATHER_API_KEY` with your API key

2. The workflow runs automatically every 30 minutes, or trigger manually:
   - Go to Actions → Update Dashboard → Run workflow

---

## Project Structure

```
weather-pipeline/
├── .github/workflows/         # GitHub Actions workflows
│   └── update-dashboard.yml   # Auto-refresh dashboard
├── dags/                      # Airflow DAG definitions
├── include/                   # Shared Python modules
│   ├── extract/               # API client, rate limiter
│   └── load/                  # PostgreSQL loader
├── dbt/                       # dbt project
│   ├── models/
│   │   ├── staging/           # Flatten raw JSON
│   │   ├── intermediate/      # Aggregations
│   │   └── marts/             # Star schema
│   └── seeds/                 # Reference data (cities)
├── sql/                       # Database init scripts
│   ├── postgres/
│   └── snowflake/
├── scripts/
│   ├── update_dashboard.py    # Fetch live data, generate HTML
│   └── seed_snowflake.py      # Initialize Snowflake schemas
├── tests/                     # Unit tests
├── docker-compose.yml         # Service orchestration
├── .env.example               # Environment template
└── README.md                  # This file
```

---

## Data Schema

### Snowflake Star Schema

```
dim_cities                    dim_dates
├── city_id (PK)              ├── date_key (PK)
├── city_name                 ├── full_date
├── country_code              ├── year, month, day
├── latitude                  ├── day_of_week
├── longitude                 └── is_weekend
└── timezone_offset

fct_weather_readings          fct_daily_weather
├── reading_id (PK)           ├── city_id (FK)
├── city_id (FK)              ├── date_key (FK)
├── date_key (FK)             ├── avg_temperature_k
├── temperature_k             ├── min_temperature_k
├── temperature_f             ├── max_temperature_k
├── humidity_pct              ├── avg_humidity_pct
├── weather_condition         └── dominant_condition
└── reading_timestamp
```

---

## Rate Limiting

| Metric | Value |
|--------|-------|
| OpenWeatherMap free tier | 1,000 calls/day |
| Pipeline per run | 5 calls (5 cities × 1 endpoint) |
| Daily usage (30-min intervals) | 240 calls (24% of budget) |
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

## Troubleshooting

### Dashboard shows old data
- Check GitHub Actions status: https://github.com/kaizen-2004/real-time-end-to-end-weather-pipeline/actions
- Ensure `OPENWEATHER_API_KEY` secret is set in repository settings
- Trigger workflow manually to test

### Airflow DAG fails
- Check Airflow UI: http://localhost:8080
- View task logs in the UI
- Ensure `.env` has correct credentials

### Snowflake connection fails
- Verify Snowflake account, user, and password in `.env`
- Check Snowflake is running and accessible
- Run `docker compose exec airflow-scheduler python /opt/airflow/scripts/seed_snowflake.py`

---

## Author

**Steve A. Villa** — BS Computer Engineering

- [Portfolio](https://steve-villa-devportfolio.netlify.app/)
- [GitHub](https://github.com/kaizen-2004)

---

## License

This project is open source and available for portfolio demonstration purposes.
