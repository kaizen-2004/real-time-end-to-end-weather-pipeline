#!/bin/bash
set -e

echo "Weather Pipeline - Setup"
echo "========================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your API keys before continuing."
    exit 1
fi

# Start Docker services
echo "Starting Docker services..."
docker compose up -d

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
sleep 5

# Wait for Airflow
echo "Waiting for Airflow to initialize..."
sleep 10

echo ""
echo "Setup complete!"
echo ""
echo "Services:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Airflow UI: http://localhost:8080 (admin / admin)"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your OpenWeatherMap API key"
echo "  2. Edit .env with your Snowflake credentials"
echo "  3. Run: python scripts/seed_snowflake.py"
echo "  4. Trigger DAG in Airflow UI"
