with source as (
    select 'regular' as season_segment, *
    from {{ source('s3__bbrewington_nhl_data__moneypuck', 'season_level/Goalies_*_regular') }}

    union all

    select 'playoffs' as season_segment, *
    from {{ source('s3__bbrewington_nhl_data__moneypuck', 'season_level/Goalies_*_playoffs') }}
),

renamed as (
    select
        season_segment,
        playerId as mp_player_id,
        season as season_yr1,
        name,
        team as team_abbr_raw,
        position,
        situation,
        games_played,
        icetime as ice_time,
        xGoals as exp_goals,
        goals,
        unblocked_shot_attempts,
        xRebounds as exp_rebounds,
        rebounds,
        xFreeze as exp_freeze,
        "freeze",
        xOnGoal as exp_on_goal,
        ongoal as on_goal,
        xPlayStopped as exp_play_stopped,
        playStopped as play_stopped,
        xPlayContinuedInZone as exp_play_continued_in_zone,
        playContinuedInZone as play_continued_in_zone,
        xPlayContinuedOutsideZone as exp_play_continued_outside_zone,
        playContinuedOutsideZone as play_continued_outside_zone,
        flurryAdjustedxGoals as flurry_adjusted_exp_goals,
        lowDangerShots as low_danger_shots,
        mediumDangerShots as medium_danger_shots,
        highDangerShots as high_danger_shots,
        lowDangerxGoals as low_danger_exp_goals,
        mediumDangerxGoals as medium_danger_exp_goals,
        highDangerxGoals as high_danger_exp_goals,
        lowDangerGoals as low_danger_goals,
        mediumDangerGoals as medium_danger_goals,
        highDangerGoals as high_danger_goals,
        blocked_shot_attempts,
        penalityMinutes as penalty_minutes,
        penalties
    from source
)

select * from renamed
