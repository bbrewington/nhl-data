with team_game as (
    select *
    from {{ ref('stg_moneypuck__team_game_situation') }}
    where situation = 'all'
),

team_abbrs as (
    select * from {{ ref('stg__team_abbrs') }}
),

teams as (
    select distinct team_abbr, team_name
    from {{ ref('stg__teams') }}
),

final as (
    select
        team_abbrs.team_abbr,
        teams.team_name,
        team_game.* exclude (team_abbr_raw)
    from team_game
    left join team_abbrs
        on team_game.team_abbr_raw = team_abbrs.team_abbr_raw
    left join teams
        on team_abbrs.team_abbr = teams.team_abbr
)

select * from final
