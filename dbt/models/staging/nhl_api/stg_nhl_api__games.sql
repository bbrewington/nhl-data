with source as (
    select * from {{ source('s3__bbrewington_nhl_data__nhl_api', 'games/game_id=*/games') }}
)

select
    cast(game_id as integer) as game_id,
    home_team_id,
    home_team_abbr,
    away_team_id,
    away_team_abbr
from source
