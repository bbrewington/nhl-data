with source as (
    select
        *,
        regexp_extract(height, '(\d)'' (\d{1,2})"', ['ft', 'in']) as height_parsed
    from {{ ref('snapshot__all_players_lookup') }}
)
select
    playerId as mp_player_id,
    name as mp_player_name,
    position,
    team as team_abbr_raw,
    birthDate as birth_date,
    weight as weight_lbs,
    height,
    (height_parsed['ft']::UTINYINT * 12 + height_parsed['in']::UTINYINT) / 12 height_ft,
    nationality,
    shootsCatches as shoots_catches,
    primaryNumber as primary_number,
    primaryPosition as primary_position,
    dbt_scd_id,
    dbt_updated_at,
    dbt_valid_from,
    dbt_valid_to,
    dbt_is_deleted
from source
