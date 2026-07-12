with source as (
    select * from {{ source('s3__bbrewington_nhl_data__nhl_api', 'boxscores/game_id=*/boxscores') }}
),

renamed as (
    select
        cast(game_id as integer) as game_id,
        playerId as player_id,
        team_id,
        position_group,
        position as position_code,
        sweaterNumber as sweater_number,
        name_default as player_name,
        starter,
        decision,
        toi,
        cast(split_part(toi, ':', 1) as integer) * 60
            + cast(split_part(toi, ':', 2) as integer) as toi_seconds,
        goals,
        assists,
        points,
        plusMinus as plus_minus,
        pim,
        hits,
        powerPlayGoals as power_play_goals,
        sog,
        faceoffWinningPctg as faceoff_winning_pctg,
        blockedShots as blocked_shots,
        shifts,
        giveaways,
        takeaways,
        shotsAgainst as shots_against,
        saves,
        savePctg as save_pctg,
        goalsAgainst as goals_against,
        evenStrengthShotsAgainst as even_strength_shots_against,
        powerPlayShotsAgainst as power_play_shots_against,
        shorthandedShotsAgainst as shorthanded_shots_against,
        saveShotsAgainst as save_shots_against,
        evenStrengthGoalsAgainst as even_strength_goals_against,
        powerPlayGoalsAgainst as power_play_goals_against,
        shorthandedGoalsAgainst as shorthanded_goals_against,

        row_number() over (
            partition by game_id, playerId order by team_id
        ) as rn
    from source
)

select * exclude (rn)
from renamed
where rn = 1
