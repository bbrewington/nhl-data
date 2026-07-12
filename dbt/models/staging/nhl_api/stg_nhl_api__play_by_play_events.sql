with source as (
    select * from {{ source('s3__bbrewington_nhl_data__nhl_api', 'play_by_play/game_id=*/play_by_play') }}
),

renamed as (
    select
        cast(game_id as integer) as game_id,
        eventId as event_id,
        periodDescriptor_number as period_number,
        periodDescriptor_periodType as period_type,
        periodDescriptor_maxRegulationPeriods as period_max_regulation_periods,
        timeInPeriod as time_in_period,
        timeRemaining as time_remaining,
        sortOrder as sort_order,
        situationCode as situation_code,
        typeCode as type_code,
        replace(typeDescKey, '-', '_') as type_desc_key,
        homeTeamDefendingSide as home_team_defending_side,

        -- situation_code is a 4-digit string: home_goalie, home_skaters, away_skaters, away_goalie
        substr(situationCode, 1, 1) = '1' as home_goalie_on_ice,
        cast(substr(situationCode, 2, 1) as integer) as home_skaters,
        cast(substr(situationCode, 3, 1) as integer) as away_skaters,
        substr(situationCode, 4, 1) = '1' as away_goalie_on_ice,

        details_eventOwnerTeamId as event_owner_team_id,
        cast(details_xCoord as float) as x_coord,
        cast(details_yCoord as float) as y_coord,
        details_zoneCode as zone_code,
        details_shotType as shot_type,
        details_shootingPlayerId as shooting_player_id,
        details_goalieInNetId as goalie_in_net_id,
        details_awaySOG as away_sog,
        details_homeSOG as home_sog,
        details_hittingPlayerId as hitting_player_id,
        details_hitteePlayerId as hittee_player_id,
        details_blockingPlayerId as blocking_player_id,
        details_playerId as player_id,
        details_winningPlayerId as winning_player_id,
        details_losingPlayerId as losing_player_id,
        details_scoringPlayerId as scoring_player_id,
        details_scoringPlayerTotal as scoring_player_total,
        details_assist1PlayerId as assist1_player_id,
        details_assist1PlayerTotal as assist1_player_total,
        details_assist2PlayerId as assist2_player_id,
        details_assist2PlayerTotal as assist2_player_total,
        details_awayScore as away_score,
        details_homeScore as home_score,
        details_typeCode as penalty_type_code,
        details_descKey as penalty_desc_key,
        details_duration as penalty_duration,
        details_committedByPlayerId as committed_by_player_id,
        details_drawnByPlayerId as drawn_by_player_id,
        details_servedByPlayerId as served_by_player_id,
        details_reason as reason,
        details_secondaryReason as secondary_reason,

        current_timestamp as loaded_at,

        row_number() over (
            partition by game_id, eventId order by sortOrder
        ) as rn
    from source
)

select * exclude (rn)
from renamed
where rn = 1
