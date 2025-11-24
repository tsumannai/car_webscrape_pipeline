{{ config(materialized='table') }}

SELECT *
FROM read_json_auto('../../data/entertainment.json')