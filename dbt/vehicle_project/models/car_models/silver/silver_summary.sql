{{ config(materialized='table') }}

SELECT
    model_key,
    model_name,
    UPPER(regexp_extract(model_name, '^([A-Za-z]+)')) AS brand,
    TRY_CAST(regexp_extract(boot_space_seats_up_litres, '([0-9.]+)') AS DOUBLE) AS boot_space_seats_up_litres,
    UPPER(TRY_CAST(insurance_group AS STRING)) AS insurance_group,
    TRY_CAST(regexp_extract(acceleration_0_62_mph_secs, '([0-9.]+)') AS DOUBLE) AS acceleration_0_62_secs,
    TRY_CAST(regexp_extract(pure_electric_range_miles, '([0-9.]+)') AS DOUBLE) AS pure_electric_range_miles,
    TRY_CAST(
        COALESCE(
            NULLIF(regexp_extract(home_charge_time, '([0-9]+) hours', 1), ''),
            '0'
        ) AS INTEGER
    ) * 60
    +
    TRY_CAST(
        COALESCE(
            NULLIF(regexp_extract(home_charge_time, '([0-9]+) mins', 1), ''),
            '0'
        ) AS INTEGER
    ) AS home_charge_time,

    TRY_CAST(
        COALESCE(
            NULLIF(regexp_extract(rapid_charge_320kw_time_mins, '([0-9]+) hours', 1), ''),
            '0'
        ) AS INTEGER
    ) * 60
    +
    TRY_CAST(
        COALESCE(
            NULLIF(regexp_extract(rapid_charge_320kw_time_mins, '([0-9]+) mins', 1), ''),
            '0'
        ) AS INTEGER
    ) AS rapid_charge_320kw_time_mins,
    scrape_timestamp
FROM {{ ref('bronze_summary') }}
QUALIFY ROW_NUMBER() OVER (PARTITION BY model_key ORDER BY scrape_timestamp DESC) = 1