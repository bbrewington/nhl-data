with enriched as (
    select * from {{ ref('int_nhl__events_enriched') }}
),

-- a new segment starts whenever strength_state or period_number changes from the prior event
ordered as (
    select
        *,
        lag(strength_state) over (partition by game_id order by sort_order) as prev_strength_state,
        lag(period_number) over (partition by game_id order by sort_order) as prev_period_number
    from enriched
),

flagged as (
    select
        *,
        case
            when prev_strength_state is null
                or strength_state != prev_strength_state
                or period_number != prev_period_number
                then 1
            else 0
        end as is_new_segment
    from ordered
),

segmented as (
    select
        *,
        sum(is_new_segment) over (
            partition by game_id order by sort_order
            rows between unbounded preceding and current row
        ) as segment_id
    from flagged
),

segment_bounds as (
    select
        game_id,
        segment_id,
        strength_state,
        period_number as period,
        min(game_seconds) as start_game_seconds
    from segmented
    group by 1, 2, 3, 4
),

-- the last event's game_seconds (typically game_end) is the total on-clock length of the game
game_lengths as (
    select
        game_id,
        max(game_seconds) as game_length_seconds
    from enriched
    group by 1
)

select
    segment_bounds.game_id,
    segment_bounds.strength_state,
    segment_bounds.period,
    segment_bounds.start_game_seconds,
    coalesce(
        lead(segment_bounds.start_game_seconds) over (
            partition by segment_bounds.game_id order by segment_bounds.segment_id
        ),
        game_lengths.game_length_seconds
    ) as end_game_seconds,
    coalesce(
        lead(segment_bounds.start_game_seconds) over (
            partition by segment_bounds.game_id order by segment_bounds.segment_id
        ),
        game_lengths.game_length_seconds
    ) - segment_bounds.start_game_seconds as duration_seconds
from segment_bounds
left join game_lengths
    on segment_bounds.game_id = game_lengths.game_id
