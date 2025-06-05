{% macro game_id_attrs(game_id_colname, indent=8) %}
substr({{ game_id_colname }}::STRING, 5, 2) as game_type,
substr({{ game_id_colname }}::STRING, 7, 4) as game_number,
if(
    substr({{ game_id_colname }}::STRING, 5, 2) = '03',
    substr({{ game_id_colname }}::STRING, 8, 1),
    NULL
)::UTINYINT as playoff_round,
if(
    substr({{ game_id_colname }}::STRING, 5, 2) = '03',
    substr(substr({{ game_id_colname }}::STRING, 7, 4), 3, 1),
    NULL
)::UTINYINT as playoff_matchup,
if(
    substr({{ game_id_colname }}::STRING, 5, 2) = '03',
    substr({{ game_id_colname }}::STRING, -1),
    NULL
)::UTINYINT as playoff_game_in_series,
{% endmacro %}
