WITH source AS (
    SELECT * FROM {{ source('raw', 'weather_forecast') }}
),
parsed AS (
    SELECT
        city_id,
        city_name,
        forecast.value:dt::INTEGER AS forecast_ts,
        TO_TIMESTAMP_NTZ(forecast.value:dt::INTEGER) AS forecast_timestamp,
        forecast.value:main.temp::FLOAT AS temperature_k,
        forecast.value:main.feels_like::FLOAT AS feels_like_k,
        forecast.value:main.temp_min::FLOAT AS temp_min_k,
        forecast.value:main.temp_max::FLOAT AS temp_max_k,
        forecast.value:main.humidity::INTEGER AS humidity_pct,
        forecast.value:main.pressure::INTEGER AS pressure_hpa,
        forecast.value:wind.speed::FLOAT AS wind_speed_ms,
        forecast.value:weather[0]:main::TEXT AS weather_condition,
        forecast.value:weather[0]:description::TEXT AS weather_description,
        forecast.value:pop::FLOAT AS precipitation_probability,
        forecast.value:clouds.all::INTEGER AS cloud_cover_pct,
        forecast.value:dt_txt::TEXT AS forecast_date_txt,
        loaded_at,
        batch_id
    FROM source,
    LATERAL FLATTEN(input => payload:list) AS forecast
    WHERE payload:list IS NOT NULL
)
SELECT * FROM parsed
