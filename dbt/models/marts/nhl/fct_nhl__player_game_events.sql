with enriched as (
    select * from {{ ref('int_nhl__events_enriched') }}
),

-- unpivot every player-involvement column in enriched into one row per (event, player, role).
-- each source column is scalar (at most one value per event), so (game_id, event_id, player_role)
-- is guaranteed unique without needing a dedup step.
player_events as (
    select game_id, event_id, type_desc_key, period_number, game_seconds, strength_state,
        shooting_player_id as player_id, 'shooter' as player_role
    from enriched where shooting_player_id is not null

    union all

    select game_id, event_id, type_desc_key, period_number, game_seconds, strength_state,
        goalie_in_net_id as player_id, 'goalie_in_net' as player_role
    from enriched where goalie_in_net_id is not null

    union all

    select game_id, event_id, type_desc_key, period_number, game_seconds, strength_state,
        hitting_player_id as player_id, 'hitter' as player_role
    from enriched where hitting_player_id is not null

    union all

    select game_id, event_id, type_desc_key, period_number, game_seconds, strength_state,
        hittee_player_id as player_id, 'hittee' as player_role
    from enriched where hittee_player_id is not null

    union all

    select game_id, event_id, type_desc_key, period_number, game_seconds, strength_state,
        blocking_player_id as player_id, 'blocker' as player_role
    from enriched where blocking_player_id is not null

    union all

    select game_id, event_id, type_desc_key, period_number, game_seconds, strength_state,
        player_id,
        case type_desc_key when 'giveaway' then 'giveaway' when 'takeaway' then 'takeaway' end as player_role
    from enriched where player_id is not null

    union all

    select game_id, event_id, type_desc_key, period_number, game_seconds, strength_state,
        winning_player_id as player_id, 'faceoff_winner' as player_role
    from enriched where winning_player_id is not null

    union all

    select game_id, event_id, type_desc_key, period_number, game_seconds, strength_state,
        losing_player_id as player_id, 'faceoff_loser' as player_role
    from enriched where losing_player_id is not null

    union all

    select game_id, event_id, type_desc_key, period_number, game_seconds, strength_state,
        scoring_player_id as player_id, 'scorer' as player_role
    from enriched where scoring_player_id is not null

    union all

    select game_id, event_id, type_desc_key, period_number, game_seconds, strength_state,
        assist1_player_id as player_id, 'assist1' as player_role
    from enriched where assist1_player_id is not null

    union all

    select game_id, event_id, type_desc_key, period_number, game_seconds, strength_state,
        assist2_player_id as player_id, 'assist2' as player_role
    from enriched where assist2_player_id is not null

    union all

    select game_id, event_id, type_desc_key, period_number, game_seconds, strength_state,
        committed_by_player_id as player_id, 'penalty_committed_by' as player_role
    from enriched where committed_by_player_id is not null

    union all

    select game_id, event_id, type_desc_key, period_number, game_seconds, strength_state,
        drawn_by_player_id as player_id, 'penalty_drawn_by' as player_role
    from enriched where drawn_by_player_id is not null

    union all

    select game_id, event_id, type_desc_key, period_number, game_seconds, strength_state,
        served_by_player_id as player_id, 'penalty_served_by' as player_role
    from enriched where served_by_player_id is not null
),

rosters as (
    select * from {{ ref('stg_nhl_api__game_rosters') }}
),

boxscores as (
    select * from {{ ref('stg_nhl_api__boxscores') }}
)

select
    player_events.game_id,
    player_events.player_id,
    rosters.team_id,
    player_events.event_id,
    player_events.type_desc_key as event_type,
    player_events.player_role,
    player_events.period_number as period,
    player_events.game_seconds,
    player_events.strength_state,
    boxscores.toi_seconds
from player_events
left join rosters
    on player_events.game_id = rosters.game_id
    and player_events.player_id = rosters.player_id
left join boxscores
    on player_events.game_id = boxscores.game_id
    and player_events.player_id = boxscores.player_id
