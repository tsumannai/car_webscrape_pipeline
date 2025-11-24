WITH duplicates AS (
    SELECT 
        model_key,
        feature_name,
        COUNT(*) AS cnt
    FROM {{ ref('vehicle_features') }}
    GROUP BY model_key, feature_name
    HAVING COUNT(*) > 1
)

SELECT *
FROM duplicates