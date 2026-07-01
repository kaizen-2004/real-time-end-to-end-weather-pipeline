SELECT DISTINCT
    city_id,
    city_name,
    country_code,
    latitude,
    longitude,
    timezone_offset,
    CURRENT_TIMESTAMP() AS loaded_at
FROM {{ ref('cities') }}
