with pbp as (
    select * from {{ ref('stg_nhl_api__play_by_play_events') }}
),

games as (
    select * from {{ ref('stg_nhl_api__games') }}
),

-- time_in_period + time_remaining is constant across all events within a period and
-- gives that period's actual length (1200s for REG/playoff-OT, 300s for regular-season OT, 0 for SO)
period_lengths as (
    select
        game_id,
        period_number,
        max(
            cast(split_part(time_in_period, ':', 1) as integer) * 60
            + cast(split_part(time_in_period, ':', 2) as integer)
            + cast(split_part(time_remaining, ':', 1) as integer) * 60
            + cast(split_part(time_remaining, ':', 2) as integer)
        ) as period_length_seconds
    from pbp
    group by 1, 2
),

period_offsets as (
    select
        game_id,
        period_number,
        coalesce(
            sum(period_length_seconds) over (
                partition by game_id order by period_number
                rows between unbounded preceding and 1 preceding
            ),
            0
        ) as game_seconds_offset
    from period_lengths
),

enriched as (
    select
        pbp.*,
        games.home_team_id,
        games.home_team_abbr,
        games.away_team_id,
        games.away_team_abbr,

        cast(pbp.event_owner_team_id as bigint) = games.home_team_id as is_home_team_event,
        case
            when cast(pbp.event_owner_team_id as bigint) = games.home_team_id then games.home_team_abbr
            when cast(pbp.event_owner_team_id as bigint) = games.away_team_id then games.away_team_abbr
        end as event_team_abbr,

        case
            when not pbp.home_goalie_on_ice or not pbp.away_goalie_on_ice then 'empty_net'
            when pbp.home_skaters = 5 and pbp.away_skaters = 5 then '5v5'
            when pbp.home_skaters = 5 and pbp.away_skaters = 4 then '5v4'
            when pbp.home_skaters = 4 and pbp.away_skaters = 5 then '4v5'
            when pbp.home_skaters = 4 and pbp.away_skaters = 4 then '4v4'
            when pbp.home_skaters = 3 and pbp.away_skaters = 3 then '3v3'
            when pbp.home_skaters = 5 and pbp.away_skaters = 3 then '5v3'
            when pbp.home_skaters = 3 and pbp.away_skaters = 5 then '3v5'
            else 'other'
        end as strength_state,

        -- home_team_defending_side is home's own defending side for the period, so home attacks the
        -- opposite side. Empirically (see Task 9 notes), attacking "right" already lands at positive
        -- raw x_coord, so a flip is only needed when the event owner's attacking side is "left".
        (
            (cast(pbp.event_owner_team_id as bigint) = games.home_team_id and pbp.home_team_defending_side = 'right')
            or (cast(pbp.event_owner_team_id as bigint) = games.away_team_id and pbp.home_team_defending_side = 'left')
        ) as coord_flip_needed,

        period_offsets.game_seconds_offset
            + cast(split_part(pbp.time_in_period, ':', 1) as integer) * 60
            + cast(split_part(pbp.time_in_period, ':', 2) as integer) as game_seconds

    from pbp
    left join games
        on pbp.game_id = games.game_id
    left join period_offsets
        on pbp.game_id = period_offsets.game_id
        and pbp.period_number = period_offsets.period_number
)

select
    * exclude (coord_flip_needed),
    case when coord_flip_needed then -1 * x_coord else x_coord end as x_coord_norm,
    case when coord_flip_needed then -1 * y_coord else y_coord end as y_coord_norm
from enriched
