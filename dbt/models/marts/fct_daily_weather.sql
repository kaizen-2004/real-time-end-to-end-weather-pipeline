WITH daily AS (
    SELECT * FROM {{ ref('int_weather__daily_summary') }}
)
SELECT
    city_id,
    TO_NUMBER(TO_CHAR(forecast_date, 'YYYYMMDD'))::INTEGER AS date_key,
    avg_temperature_k,
    min_temperature_k,
    max_temperature_k,
    avg_humidity_pct,
    avg_wind_speed_ms,
    max_precipitation_probability,
    dominant_condition,
    forecast_count AS reading_count,
    CURRENT_TIMESTAMP() AS loaded_at
FROM daily
