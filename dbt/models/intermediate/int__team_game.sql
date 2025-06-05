select *
from {{ ref('stg_moneypuck__team_game_situation') }}
where situation = 'all'
