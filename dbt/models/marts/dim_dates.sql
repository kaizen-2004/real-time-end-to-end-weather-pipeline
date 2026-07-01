WITH date_series AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY seq4()) AS row_num,
        DATEADD(DAY, ROW_NUMBER() OVER (ORDER BY seq4()), '2024-01-01'::DATE) AS full_date
    FROM TABLE(GENERATOR(ROWCOUNT => 365 * 3))
)
SELECT
    TO_NUMBER(TO_CHAR(full_date, 'YYYYMMDD'))::INTEGER AS date_key,
    full_date,
    EXTRACT(YEAR FROM full_date)::INTEGER AS year,
    EXTRACT(MONTH FROM full_date)::INTEGER AS month,
    EXTRACT(DAY FROM full_date)::INTEGER AS day,
    EXTRACT(DAYOFWEEK FROM full_date)::INTEGER AS day_of_week,
    DAYNAME(full_date) AS day_name,
    MONTHNAME(full_date) AS month_name,
    QUARTER(full_date)::INTEGER AS quarter,
    CASE WHEN EXTRACT(DAYOFWEEK FROM full_date) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend
FROM date_series
