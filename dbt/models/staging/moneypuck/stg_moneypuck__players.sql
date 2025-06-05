select * exclude(
    dbt_scd_id,
    dbt_updated_at,
    dbt_valid_from,
    dbt_valid_to,
    dbt_is_deleted
)
from {{ ref('stg_moneypuck__players_hist') }}
where dbt_valid_to is null
and dbt_is_deleted = FALSE
