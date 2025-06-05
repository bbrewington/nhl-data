select 'regular' as season_segment, *
from {{ source('s3__bbrewington_nhl_data__moneypuck', 'season_level/Lines_*_regular') }}

union all

select 'playoffs' as season_segment, *
from {{ source('s3__bbrewington_nhl_data__moneypuck', 'season_level/Lines_*_playoffs') }}
