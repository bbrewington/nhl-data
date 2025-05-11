select
    tg.team_abbr,
    tm.team_name,
    tm.min_season,
    tm.max_season,
    tm.max_season is null as active_flag,
from {{ ref('stg__mp__team_game_situation') }} as tg
left join {{ ref('seed__team') }} as tm
    using(team_abbr)
group by all