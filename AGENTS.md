# AGENTS.md — Weather Pipeline

## Project Context

Real-time ELT data pipeline: OpenWeatherMap API → PostgreSQL → dbt → Snowflake, orchestrated with Apache Airflow on Docker.

## Rules

- Follow the sprint plan in `SPRINT_PLAN.md` — complete sprints in order (0 → 7).
- Do not skip ahead to implement features from future sprints.
- Each sprint must be verified working before moving to the next.
- Use Python 3.11+ type hints in all Python code.
- Keep Docker services portable — no hardcoded hostnames outside docker-compose network.
- PostgreSQL uses port 5433 externally (5432 internally in Docker network).
- All API keys and secrets go in `.env` (never commit `.env`).
- Use `requests` for HTTP calls, `psycopg2` for PostgreSQL, `snowflake-connector-python` for Snowflake.
- dbt models follow the naming convention: `stg_` (staging), `int_` (intermediate), `fct_`/`dim_` (marts).
- DAGs must include `retries`, `retry_delay`, and `execution_timeout` in `default_args`.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Data Source | OpenWeatherMap API (free tier: 1000 calls/day) |
| Orchestration | Apache Airflow 2.9 |
| Staging DB | PostgreSQL 16 (Docker) |
| Transformation | dbt 1.7 |
| Warehouse | Snowflake (free trial) |
| Containerization | Docker Compose |

## Running Services

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f airflow-webserver

# Access Airflow UI
open http://localhost:8080  # admin / admin

# Access PostgreSQL
docker compose exec postgres psql -U weather_user -d weather_staging
```

## Sprint Progress

See `SPRINT_PLAN.md` for full sprint details. Current status:
- Sprint 0: ✅ DONE
- Sprint 1: ✅ DONE
- Sprint 2: ✅ DONE
- Sprint 3: ✅ DONE
- Sprint 4: ✅ DONE
- Sprint 5: ✅ DONE
- Sprint 6: ✅ DONE
- Sprint 7: ✅ DONE

All sprints complete! Project is portfolio-ready.
