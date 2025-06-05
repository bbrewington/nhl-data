with source as (
    select
        team_abbr,
        team_name,
        min_season,
        max_season,
        max_season is null as is_active
    from {{ ref('seed__teams') }}
),

final as (
    select
        team_abbr,
        team_name,
        is_active,
        -- note, doing this min & max b/c the seed has duplicate rows capturing the different
        -- team abbreviations (e.g. team_abbr_raw: S.J, team_abbr: SJS)
        min(min_season) as min_season,
        max(max_season) as max_season
    from source
    group by 1,2,3
)

select * from final