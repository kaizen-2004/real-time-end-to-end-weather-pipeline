# Architecture Overview

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA FLOW PIPELINE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. TRIGGER                                                        │
│     Airflow scheduler (*/30)                                       │
│     ──────────────────────────────────────────────                  │
│                                                                     │
│  2. EXTRACT                                                        │
│     weather_api.py → OpenWeatherMap REST API                       │
│     • GET /data/2.5/weather?lat={lat}&lon={lon}                    │
│     • GET /data/2.5/forecast?lat={lat}&lon={lon}                   │
│     • Rate limiter: max 1000 calls/day, 60 calls/min              │
│     • Retry: exponential backoff, max 3 retries                   │
│     ──────────────────────────────────────────────                  │
│                                                                     │
│  3. LOAD → PostgreSQL (staging)                                    │
│     postgres_loader.py → raw schema                                │
│     • raw.weather_current (JSONB payload)                          │
│     • raw.weather_forecast (JSONB payload)                         │
│     ──────────────────────────────────────────────                  │
│                                                                     │
│  4. TRANSFORM → dbt                                                │
│     models/staging/    → Flatten JSONB into structured columns     │
│     models/intermediate/ → Aggregate hourly/daily summaries        │
│     models/marts/     → Star schema (dim_cities, fct_readings)    │
│     ──────────────────────────────────────────────                  │
│                                                                     │
│  5. LOAD → Snowflake                                               │
│     dbt run writes to Snowflake:                                   │
│     • raw.weather_current                                          │
│     • raw.weather_forecast                                         │
│     • marts.dim_cities                                             │
│     • marts.dim_dates                                              │
│     • marts.fct_weather_readings                                   │
│     • marts.fct_daily_weather                                      │
│     ──────────────────────────────────────────────                  │
│                                                                     │
│  6. TEST                                                           │
│     dbt test: row counts, uniqueness, not-null                     │
│     Airflow: check sensors for data freshness                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Schema Design

### PostgreSQL (Staging)

**raw.weather_current**
- Stores full API response as JSONB
- Indexed on `fetched_at` for time-based queries
- Batch ID for tracking load operations

**raw.weather_forecast**
- Stores forecast API response as JSONB
- Same structure as current weather

### Snowflake (Star Schema)

**Dimensions:**
- `dim_cities` — City lookup with coordinates and timezone
- `dim_dates` — Date dimension for time-based analysis

**Facts:**
- `fct_weather_readings` — Current weather observations with temperature conversions
- `fct_daily_weather` — Daily weather summaries per city

## Design Decisions

### Why ELT over ETL?
- Load raw data first, transform in the warehouse
- Preserves raw data for debugging and reprocessing
- dbt handles transformations declaratively in SQL

### Why JSONB in PostgreSQL?
- Flexible schema for evolving API responses
- Easy to query specific fields
- Natural landing zone for API data

### Why Star Schema in Snowflake?
- Optimized for analytical queries
- Clear separation of dimensions and facts
- Industry standard for data warehousing

## Rate Limiting Strategy

- **OpenWeatherMap free tier**: 1,000 API calls/day
- **Pipeline**: 5 cities × 2 endpoints = 10 calls per run
- **At 30-min intervals**: 48 runs/day = 480 calls/day (48% of budget)
- **Built-in rate limiter**: max 60 calls/minute with automatic backoff
