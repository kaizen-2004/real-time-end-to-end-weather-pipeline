CREATE TABLE raw.weather_current (
    id              INTEGER AUTOINCREMENT PRIMARY KEY,
    city_id         INTEGER,
    city_name       TEXT,
    payload         VARIANT NOT NULL,
    loaded_at       TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    batch_id        TEXT
);

CREATE TABLE raw.weather_forecast (
    id              INTEGER AUTOINCREMENT PRIMARY KEY,
    city_id         INTEGER,
    city_name       TEXT,
    payload         VARIANT NOT NULL,
    loaded_at       TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    batch_id        TEXT
);
