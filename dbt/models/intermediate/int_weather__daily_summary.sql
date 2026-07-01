SELECT
    city_id,
    city_name,
    DATE(forecast_timestamp) AS forecast_date,
    AVG(temperature_k) AS avg_temperature_k,
    MIN(temperature_k) AS min_temperature_k,
    MAX(temperature_k) AS max_temperature_k,
    AVG(humidity_pct) AS avg_humidity_pct,
    AVG(wind_speed_ms) AS avg_wind_speed_ms,
    MAX(precipitation_probability) AS max_precipitation_probability,
    MODE(weather_condition) AS dominant_condition,
    COUNT(*) AS forecast_count
FROM {{ ref('stg_weather__forecast') }}
GROUP BY 1, 2, 3
