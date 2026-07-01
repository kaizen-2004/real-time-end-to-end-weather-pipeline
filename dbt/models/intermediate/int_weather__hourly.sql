SELECT
    city_id,
    city_name,
    forecast_timestamp,
    DATE_TRUNC('HOUR', forecast_timestamp) AS forecast_hour,
    AVG(temperature_k) AS avg_temperature_k,
    AVG(humidity_pct) AS avg_humidity_pct,
    AVG(wind_speed_ms) AS avg_wind_speed,
    MAX(precipitation_probability) AS max_pop,
    MODE() WITHIN GROUP (ORDER BY weather_condition) AS dominant_condition
FROM {{ ref('stg_weather__forecast') }}
GROUP BY 1, 2, 3, 4
