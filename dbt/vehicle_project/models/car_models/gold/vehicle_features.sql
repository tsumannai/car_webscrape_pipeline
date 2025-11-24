{{ config(materialized='table') }}

WITH summary AS (
    SELECT 
    model_key,
    model_name,
    brand AS manufacturer,
    pure_electric_range_miles AS range,
    FROM {{ ref('silver_summary') }}
)
,
entertainment AS
(
    SELECT 
    model_key,
    feature_name,
    feature_value
    FROM {{ ref('silver_entertainment') }} 
    UNPIVOT (
        feature_value for feature_name in (
            third_party_sound_system,
            digital_radio,
            radio,
            oem_sound_system
        )
    )
)
,
interior AS
(
    SELECT 
    model_key,
    feature_name,
    feature_value
    FROM {{ ref('silver_interior') }} 
    UNPIVOT (
        feature_value for feature_name in (
            second_row_three_seat_bench,
            three_zone_climate_control,
            rear_seat_belts_3x3_point,
            air_conditioning,
            alloy_pedals,
            front_head_restraints,
            heat_pump,
            isofix_child_anchor_points,
            single_front_passenger_seat,
            split_folding_rear_seat,
            steering_wheel_manually_adjustable,
            textile_floor_mats,
            electrically_adjustable_drivers_seat,
            heated_rear_seats,
            ventilated_front_seats,
            heated_front_seat,
            leather_artificial_leather_upholstery,
        )
    )
)
SELECT
s.*,
feature_name,
feature_value
FROM summary s
LEFT JOIN 
    (
        (SELECT *  FROM entertainment)
    UNION ALL
        (SELECT *  FROM interior)
    ) f
ON f.model_key = s.model_key