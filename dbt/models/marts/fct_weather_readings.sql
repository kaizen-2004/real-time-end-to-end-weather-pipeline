WITH current_data AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['city_id', 'reading_timestamp']) }} AS reading_id,
        city_id,
        TO_NUMBER(TO_CHAR(DATE(reading_timestamp), 'YYYYMMDD'))::INTEGER AS date_key,
        reading_timestamp,
        temperature_k,
        ROUND(temperature_k - 273.15, 2) AS temperature_c,
        ROUND((temperature_k - 273.15) * 9/5 + 32, 2) AS temperature_f,
        feels_like_k,
        humidity_pct,
        pressure_hpa,
        wind_speed_ms,
        wind_deg,
        weather_condition,
        weather_description,
        cloud_cover_pct,
        visibility_m,
        loaded_at,
        batch_id
    FROM {{ ref('stg_weather__current') }}
)
SELECT * FROM current_data
