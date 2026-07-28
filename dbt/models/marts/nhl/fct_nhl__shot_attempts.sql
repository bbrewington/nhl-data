with shots as (
    select * from {{ ref('int_nhl__shot_events') }}
),

games as (
    select * from {{ ref('stg_nhl_api__games') }}
)

select
    shots.game_id,
    shots.event_id,
    shots.shooter_player_id as player_id,
    case when shots.is_home_team_event then games.home_team_id else games.away_team_id end as team_id,
    case when shots.is_home_team_event then games.away_team_id else games.home_team_id end as opponent_team_id,
    shots.period_number as period,
    shots.game_seconds,
    shots.strength_state,
    shots.shot_type,
    shots.shot_distance,
    shots.shot_angle,
    shots.x_coord_norm as x_coord,
    shots.y_coord_norm as y_coord,
    shots.is_corsi_event,
    shots.is_fenwick_event,
    shots.is_shot_on_goal,
    shots.is_goal,
    shots.is_rebound,
    shots.is_rush_shot,
    shots.is_home_team_event as is_home_event,
    shots.zone_code
from shots
left join games
    on shots.game_id = games.game_id
