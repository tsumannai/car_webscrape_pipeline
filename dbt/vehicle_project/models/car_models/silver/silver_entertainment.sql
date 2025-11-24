{{ config(materialized='table') }}

SELECT
    model_key,
    model_name,
    TRY_CAST(third_party_sound_system AS BOOL) AS third_party_sound_system,
    TRY_CAST(digital_radio AS BOOL) AS digital_radio,
    TRY_CAST(radio AS BOOL) AS radio,
    TRY_CAST(oem_sound_system AS BOOL) AS oem_sound_system,
    scrape_timestamp
FROM {{ ref('bronze_entertainment') }}
QUALIFY ROW_NUMBER() OVER (PARTITION BY model_key ORDER BY scrape_timestamp DESC) = 1