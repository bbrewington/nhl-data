with players as (
    select * from {{ ref('stg_moneypuck__players') }}
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
        players.mp_player_id,
        players.mp_player_name,
        players.position,
        players.primary_position,
        players.primary_number,
        players.birth_date,
        date_diff('year', players.birth_date, current_date) as age,
        players.height,
        players.height_ft,
        players.weight_lbs,
        players.nationality,
        players.shoots_catches,
        team_abbrs.team_abbr,
        teams.team_name
    from players
    left join team_abbrs
        on players.team_abbr_raw = team_abbrs.team_abbr_raw
    left join teams
        on team_abbrs.team_abbr = teams.team_abbr
)

select * from final
