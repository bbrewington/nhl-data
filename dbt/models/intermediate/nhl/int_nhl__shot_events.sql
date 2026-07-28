with enriched as (
    select * from {{ ref('int_nhl__events_enriched') }}
),

events_ordered as (
    select
        *,
        type_desc_key in ('shot_on_goal', 'goal', 'missed_shot', 'blocked_shot') as is_shot_attempt,
        lag(zone_code) over (partition by game_id order by sort_order) as prev_event_zone_code,
        lag(game_seconds) over (partition by game_id order by sort_order) as prev_event_game_seconds
    from enriched
),

-- last shot-attempt's game_seconds strictly before the current row, regardless of which team took it
with_prev_shot_attempt as (
    select
        *,
        max(case when is_shot_attempt then game_seconds end) over (
            partition by game_id order by sort_order
            rows between unbounded preceding and 1 preceding
        ) as prev_shot_attempt_game_seconds
    from events_ordered
)

select
    game_id,
    event_id,
    period_number,
    game_seconds,
    strength_state,
    is_home_team_event,
    event_team_abbr,
    coalesce(scoring_player_id, shooting_player_id) as shooter_player_id,
    shot_type,
    zone_code,
    x_coord_norm,
    y_coord_norm,

    type_desc_key = 'blocked_shot' as is_blocked_shot,
    true as is_corsi_event,
    type_desc_key != 'blocked_shot' as is_fenwick_event,
    type_desc_key in ('shot_on_goal', 'goal') as is_shot_on_goal,
    type_desc_key = 'goal' as is_goal,

    sqrt(power(89 - abs(x_coord_norm), 2) + power(y_coord_norm, 2)) as shot_distance,
    degrees(atan2(y_coord_norm, 89 - abs(x_coord_norm))) as shot_angle,

    coalesce(
        game_seconds - prev_shot_attempt_game_seconds <= 3, false
    ) as is_rebound,
    coalesce(
        game_seconds - prev_event_game_seconds <= 4
        and zone_code != prev_event_zone_code,
        false
    ) as is_rush_shot

from with_prev_shot_attempt
where is_shot_attempt
