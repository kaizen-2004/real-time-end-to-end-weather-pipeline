CREATE TABLE raw.weather_current (
    id              SERIAL PRIMARY KEY,
    city_id         INTEGER,
    city_name       TEXT,
    country_code    TEXT,
    latitude        NUMERIC(9,6),
    longitude       NUMERIC(9,6),
    payload         JSONB NOT NULL,
    fetched_at      TIMESTAMPTZ DEFAULT NOW(),
    load_batch_id   UUID DEFAULT gen_random_uuid()
);

CREATE TABLE raw.weather_forecast (
    id              SERIAL PRIMARY KEY,
    city_id         INTEGER,
    city_name       TEXT,
    latitude        NUMERIC(9,6),
    longitude       NUMERIC(9,6),
    payload         JSONB NOT NULL,
    fetched_at      TIMESTAMPTZ DEFAULT NOW(),
    load_batch_id   UUID DEFAULT gen_random_uuid()
);

CREATE INDEX idx_raw_current_fetched ON raw.weather_current(fetched_at);
CREATE INDEX idx_raw_forecast_fetched ON raw.weather_forecast(fetched_at);
