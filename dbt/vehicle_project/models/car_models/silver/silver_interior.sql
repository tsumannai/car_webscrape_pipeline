{{ config(materialized='table') }}

SELECT
    model_key,
    model_name,
    TRY_CAST(second_row_three_seat_bench AS BOOL) AS second_row_three_seat_bench,
    TRY_CAST(three_zone_climate_control AS BOOL) AS three_zone_climate_control,
    TRY_CAST(rear_seat_belts_3x3_point AS BOOL) AS rear_seat_belts_3x3_point,
    TRY_CAST(air_conditioning AS BOOL) AS air_conditioning,
    TRY_CAST(alloy_pedals AS BOOL) AS alloy_pedals,
    TRY_CAST(front_head_restraints AS BOOL) AS front_head_restraints,
    TRY_CAST(heat_pump AS BOOL) AS heat_pump,
    TRY_CAST(isofix_child_anchor_points AS BOOL) AS isofix_child_anchor_points,
    TRY_CAST(single_front_passenger_seat AS BOOL) AS single_front_passenger_seat,
    TRY_CAST(split_folding_rear_seat AS BOOL) AS split_folding_rear_seat,
    TRY_CAST(steering_wheel_manually_adjustable AS BOOL) AS steering_wheel_manually_adjustable,
    TRY_CAST(textile_floor_mats AS BOOL) AS textile_floor_mats,
    TRY_CAST(electrically_adjustable_drivers_seat AS BOOL) AS electrically_adjustable_drivers_seat,
    TRY_CAST(heated_rear_seats AS BOOL) AS heated_rear_seats,
    TRY_CAST(ventilated_front_seats AS BOOL) AS ventilated_front_seats,
    TRY_CAST(heated_front_seat AS BOOL) AS heated_front_seat,
    TRY_CAST(leather_artificial_leather_upholstery AS BOOL) AS leather_artificial_leather_upholstery,
    scrape_timestamp
FROM {{ ref('bronze_interior') }}
QUALIFY ROW_NUMBER() OVER (PARTITION BY model_key ORDER BY scrape_timestamp DESC) = 1