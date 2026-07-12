with source as (
    select * from {{ source('s3__bbrewington_nhl_data__nhl_api', 'game_rosters/game_id=*/game_rosters') }}
),

renamed as (
    select
        cast(game_id as integer) as game_id,
        playerId as player_id,
        teamId as team_id,
        positionCode as position_code,
        sweaterNumber as sweater_number,
        firstName_default as first_name,
        lastName_default as last_name,

        row_number() over (
            partition by game_id, playerId order by teamId
        ) as rn
    from source
)

select * exclude (rn)
from renamed
where rn = 1
