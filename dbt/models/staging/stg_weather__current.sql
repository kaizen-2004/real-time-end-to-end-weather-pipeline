WITH source AS (
    SELECT * FROM {{ source('raw', 'weather_current') }}
),
parsed AS (
    SELECT
        city_id,
        city_name,
        payload:main.temp::FLOAT AS temperature_k,
        payload:main.feels_like::FLOAT AS feels_like_k,
        payload:main.humidity::INTEGER AS humidity_pct,
        payload:main.pressure::INTEGER AS pressure_hpa,
        payload:wind.speed::FLOAT AS wind_speed_ms,
        payload:wind.deg::INTEGER AS wind_deg,
        payload:weather[0]:main::TEXT AS weather_condition,
        payload:weather[0]:description::TEXT AS weather_description,
        payload:clouds.all::INTEGER AS cloud_cover_pct,
        payload:visibility::INTEGER AS visibility_m,
        TO_TIMESTAMP_NTZ(payload:dt::INTEGER) AS reading_timestamp,
        loaded_at,
        batch_id
    FROM source
    WHERE payload IS NOT NULL
)
SELECT * FROM parsed
