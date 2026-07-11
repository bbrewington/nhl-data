select distinct
    team_abbr_raw,
    team_abbr
from {{ ref('seed__teams') }}
