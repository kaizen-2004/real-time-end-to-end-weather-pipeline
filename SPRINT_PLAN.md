# Weather Pipeline — Sprint Plan

## Overview
End-to-end near real-time data pipeline: OpenWeatherMap → PostgreSQL → dbt → Snowflake, orchestrated with Apache Airflow on Docker.

**Location:** `projects/weather-pipeline/`
**Cadence:** Flexible sprints (1-2 hours per session, not strictly daily)

---

## Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  OpenWeather │───→│  PostgreSQL  │───→│     dbt      │───→│   Snowflake  │
│     API      │    │   (staging)  │    │  (transform) │    │  (warehouse) │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
   Every 30 min       JSONB landing      Star schema          Analytics-ready
                      zone               ELT models           data warehouse
```

---

## Sprint 0: Environment Setup ✅ DONE

**Goal:** Working Docker stack with PostgreSQL and Airflow running locally

### Tasks

| # | Task | Status |
|---|------|--------|
| 0.1 | Create directory structure under `projects/weather-pipeline/` | ✅ |
| 0.2 | Write `.env.example` with all required variables | ✅ |
| 0.3 | Write `.gitignore` | ✅ |
| 0.4 | Write `docker-compose.yml` with PostgreSQL + Airflow services | ✅ |
| 0.5 | Write `Dockerfile.airflow` with required providers | ✅ |
| 0.6 | Write `requirements-airflow.txt` | ✅ |
| 0.7 | Verify Docker stack starts cleanly | ✅ |

**Sprint Done When:** You can open Airflow UI, see admin dashboard, and PostgreSQL accepts connections.

---

## Sprint 1: PostgreSQL Schema + Data Extraction ✅ DONE

**Goal:** Weather API client that extracts data and loads raw JSON into PostgreSQL

### Tasks

| # | Task | Acceptance Criteria |
|---|------|---------------------|
| 1.1 | Write `sql/postgres/00_init_schemas.sql` | Creates `raw` and `staging` schemas |
| 1.2 | Write `sql/postgres/01_create_tables.sql` | Creates `raw.weather_current` and `raw.weather_forecast` with JSONB `payload` column |
| 1.3 | Write `config/cities.json` with 5 cities | Contains: Rome, London, Paris, Prague, New York with lat/lon |
| 1.4 | Write `include/extract/weather_api.py` | `WeatherAPIClient` class with `get_current()` and `get_forecast()` methods |
| 1.5 | Write `include/extract/rate_limiter.py` | `RateLimiter` class that enforces max 60 calls/minute |
| 1.6 | Write `include/load/postgres_loader.py` | `PostgresLoader` class with `load_current()` and `load_forecast()` methods |
| 1.7 | Test: Manual extract + load to PostgreSQL | Run script, verify `raw.weather_current` and `raw.weather_forecast` contain JSONB data |

**Sprint Done When:** You can run a Python script that calls OpenWeatherMap API and stores raw JSON responses in PostgreSQL.

---

## Sprint 2: Airflow DAG ✅ DONE

**Goal:** Automated pipeline that runs every 30 minutes via Airflow

### Tasks

| # | Task | Acceptance Criteria |
|---|------|---------------------|
| 2.1 | Write `dags/__init__.py` | Empty init file |
| 2.2 | Write `dags/weather_pipeline.py` | DAG with: `extract_current`, `extract_forecast`, `dbt_run` tasks |
| 2.3 | Configure Airflow PostgreSQL connection | Connection `postgres_default` works in Airflow UI |
| 2.4 | Test: DAG appears in Airflow UI | DAG `weather_pipeline` shows up, is enabled, no import errors |
| 2.5 | Test: Manual DAG run | Trigger DAG manually, verify data lands in PostgreSQL |

**Sprint Done When:** You can trigger the DAG from Airflow UI and see weather data in PostgreSQL.

---

## Sprint 3: dbt Project Setup ✅ DONE

**Goal:** dbt project that connects to Snowflake and runs models

### Tasks

| # | Task | Acceptance Criteria |
|---|------|---------------------|
| 3.1 | Write `dbt/dbt_project.yml` | Project config with staging/intermediate/marts model paths |
| 3.2 | Write `dbt/profiles.yml` | Snowflake connection using env vars |
| 3.3 | Write `Dockerfile.dbt` | Python 3.11 image with `dbt-snowflake` installed |
| 3.4 | Add dbt-runner service to `docker-compose.yml` | `docker compose run dbt-runner dbt --version` works |
| 3.5 | Write `sql/snowflake/00_init_schemas.sql` | Creates `raw`, `staging`, `marts` schemas |
| 3.6 | Write `sql/snowflake/01_create_tables.sql` | Creates raw tables (weather_current, weather_forecast) with VARIANT payload |
| 3.7 | Write `scripts/seed_snowflake.py` | Script that connects to Snowflake and runs init SQL |
| 3.8 | Test: `dbt debug` passes | dbt connects to Snowflake successfully |

**Sprint Done When:** dbt connects to Snowflake and you can run `dbt debug` without errors.

---

## Sprint 4: dbt Staging Models ✅ DONE

**Goal:** Flatten raw JSONB/VARIANT data into structured staging views

### Tasks

| # | Task | Acceptance Criteria |
|---|------|---------------------|
| 4.1 | Write `dbt/models/staging/_staging__sources.yml` | Defines `raw.weather_current` and `raw.weather_forecast` as sources |
| 4.2 | Write `dbt/models/staging/stg_weather__current.sql` | Flattens JSON payload into typed columns (temperature, humidity, wind, etc.) |
| 4.3 | Write `dbt/models/staging/stg_weather__forecast.sql` | Flattens forecast list using `LATERAL FLATTEN`, extracts hourly forecasts |
| 4.4 | Test: `dbt run --select staging` | Both staging models materialize as views in Snowflake |
| 4.5 | Test: `dbt test --select staging` | Source freshness checks pass |

**Sprint Done When:** Staging models exist in Snowflake and can be queried with `SELECT * FROM staging.stg_weather__current`.

---

## Sprint 5: dbt Intermediate + Mart Models ✅ DONE

**Goal:** Star schema in Snowflake with dimensions and facts

### Tasks

| # | Task | Acceptance Criteria |
|---|------|---------------------|
| 5.1 | Write `dbt/models/intermediate/int_weather__hourly.sql` | Aggregates forecast data to hourly granularity |
| 5.2 | Write `dbt/models/intermediate/int_weather__daily_summary.sql` | Aggregates to daily min/max/avg temperature |
| 5.3 | Write `dbt/models/marts/dim_cities.sql` | City dimension with coordinates and timezone |
| 5.4 | Write `dbt/models/marts/dim_dates.sql` | Date dimension using Snowflake `GENERATOR` |
| 5.5 | Write `dbt/models/marts/fct_weather_readings.sql` | Current weather fact with temperature conversions (K→F) |
| 5.6 | Write `dbt/models/marts/fct_daily_weather.sql` | Daily weather summary fact |
| 5.7 | Write `dbt/seeds/cities.csv` | Seed data for 5 cities |
| 5.8 | Test: `dbt run` completes | All models materialize in Snowflake |
| 5.9 | Test: `dbt test` passes | All tests (uniqueness, not-null) pass |

**Sprint Done When:** Star schema exists in Snowflake with dim_cities, dim_dates, fct_weather_readings, fct_daily_weather.

---

## Sprint 6: Integration + End-to-End Test ✅ DONE

**Goal:** Full pipeline runs automatically from API → PostgreSQL → Snowflake

### Tasks

| # | Task | Acceptance Criteria |
|---|------|---------------------|
| 6.1 | Update Airflow DAG to include dbt tasks | DAG has: extract → load → dbt_run_staging → dbt_run_marts |
| 6.2 | Write `scripts/setup.sh` | One-command setup: copy .env, start docker, init snowflake |
| 6.3 | Test: Full pipeline run | Trigger DAG, verify data flows through entire stack |
| 6.4 | Test: Query Snowflake | `SELECT * FROM marts.fct_weather_readings` returns weather data |
| 6.5 | Test: Verify rate limiting | Check logs show rate limiter working correctly |

**Sprint Done When:** You can trigger one DAG run and see fresh weather data in Snowflake star schema.

---

## Sprint 7: Documentation + Portfolio Polish ✅ DONE

**Goal:** Portfolio-ready project with README, architecture docs, and screenshots

### Tasks

| # | Task | Acceptance Criteria |
|---|------|---------------------|
| 7.1 | Write `README.md` | Includes: overview, architecture diagram, tech stack, quick start, sample queries |
| 7.2 | Write `docs/architecture.md` | Detailed data flow, schema diagrams, design decisions |
| 7.3 | Take screenshots | Airflow UI, DAG run, Snowflake query results |
| 7.4 | Write `tests/test_weather_api.py` | Unit tests for API client |
| 7.5 | Write `tests/test_dag_integrity.py` | Validates DAG imports without errors |
| 7.6 | Final integration test | Full pipeline runs end-to-end without manual intervention |

**Sprint Done When:** README is complete, screenshots are taken, all tests pass.

---

## Sprint Summary

| Sprint | Focus | Sessions | Key Deliverable | Status |
|--------|-------|----------|-----------------|--------|
| 0 | Environment | 1-2 | Docker stack running | ✅ DONE |
| 1 | Extraction | 2-3 | API client + PostgreSQL loading | ✅ DONE |
| 2 | Orchestration | 1-2 | Airflow DAG automated | ✅ DONE |
| 3 | dbt Setup | 1-2 | dbt connects to Snowflake | ✅ DONE |
| 4 | Staging | 1-2 | Flattened staging views | ✅ DONE |
| 5 | Marts | 2-3 | Star schema in Snowflake | ✅ DONE |
| 6 | Integration | 1-2 | End-to-end pipeline | ✅ DONE |
| 7 | Documentation | 1-2 | Portfolio-ready project | ✅ DONE |

**Total estimated sessions:** 10-18 (at 1-2 hours each)

---

## Definition of Done (Per Sprint)

- [ ] All tasks in sprint have acceptance criteria met
- [ ] Code committed to git with descriptive messages
- [ ] No errors in Docker logs
- [ ] Manual verification of output (query DB, check UI)

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Data Source | OpenWeatherMap API | Weather forecasts (free tier: 1000 calls/day) |
| Orchestration | Apache Airflow 2.9 | Schedule and monitor pipeline |
| Staging DB | PostgreSQL 16 (Docker) | Landing zone for raw JSON |
| Transformation | dbt 1.7 | SQL models, tests, documentation |
| Warehouse | Snowflake (free trial) | Analytics-ready star schema |
| Containerization | Docker Compose | Reproducible local dev |

---

## Key Design Decisions

- **ELT over ETL**: Load raw data first, transform in the warehouse
- **JSONB in PostgreSQL**: Flexible schema for evolving API responses
- **Star Schema in Snowflake**: Optimized for analytical queries
- **30-minute schedule**: Balances freshness with rate limits (480 calls/day = 48% of budget)
- **5 cities**: Rome, London, Paris, Prague, New York
