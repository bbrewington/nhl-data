# Spec: NHL Play-by-Play Data Pipeline

## Overview

Add NHL play-by-play event data to an existing hockey analytics warehouse. This is the highest-value next dataset - it unlocks nearly every advanced hockey analytic (Corsi, Fenwick, xG, shot quality, situational analysis).

The existing project already ingests player, team, and game data from the NHL Stats API using dlt (data load tool) into DuckDB, with dbt models layered on top.

## Goals

- Ingest play-by-play events and boxscore data from the NHL Web API
- Model events into analytics-ready tables for shot analysis, on-ice impact, and strength-state breakdowns
- Maintain incremental loading - only fetch new/updated games
- Follow the project's existing patterns: uv for Python, dlt for ingestion, dbt with DuckDB for modeling

## Out of Scope (for now)

- Expected goals (xG) model - future iteration built on top of `fct_nhl__shot_attempts`
- Shift-by-shift data - separate pipeline
- Salary cap / contract data - separate source

---

## Data Source: NHL Web API

Base URL: `https://api-web.nhle.com/v1`

No authentication required. No official docs - reference the community-maintained [NHL-API-Reference](https://github.com/Zmalski/NHL-API-Reference).

### Endpoints

**Play-by-Play** - `GET /v1/gamecenter/{game-id}/play-by-play`

Returns all events for a game. Response size: 200KB - 800KB per game. Key response structure:

```
{
  "id": 2024020240,
  "gameType": 2,               // 2 = regular season, 3 = playoffs
  "season": 20242025,
  "periodDescriptor": { ... },
  "clock": { ... },
  "rosterSpots": [ ... ],      // team rosters for the game
  "plays": [                   // all game events
    {
      "eventId": 1,
      "periodDescriptor": {
        "number": 1,
        "periodType": "REG"    // REG, OT, SO
      },
      "timeInPeriod": "01:23",
      "timeRemaining": "18:37",
      "situationCode": "1551", // home_goalie, home_skaters, away_skaters, away_goalie
      "typeCode": 505,
      "typeDescKey": "shot-on-goal",  // event type string
      "details": {
        "xCoord": 72,          // x coordinate, centered on center ice
        "yCoord": -12,         // y coordinate
        "zoneCode": "O",       // O = offensive, D = defensive, N = neutral
        "shootingPlayerId": 8478402,
        "goalieInNetId": 8477970,
        "shotType": "wrist",
        "eventOwnerTeamId": 22
      }
    },
    ...
  ]
}
```

Key event types (`typeDescKey`): `faceoff`, `hit`, `giveaway`, `takeaway`, `shot-on-goal`, `goal`, `missed-shot`, `blocked-shot`, `penalty`, `stoppage`, `period-start`, `period-end`, `game-end`, `delayed-penalty`, `failed-shot-attempt`

**Boxscore** - `GET /v1/gamecenter/{game-id}/boxscore`

Player-level game stats grouped by team and position. Key structure:

```
{
  "playerByGameStats": {
    "awayTeam": {
      "forwards": [ { "playerId": ..., "sweaterNumber": ..., "toi": "18:42", "goals": 1, "assists": 0, "shots": 4, "hits": 2, ... } ],
      "defense": [ ... ],
      "goalies": [ ... ]
    },
    "homeTeam": { ... }
  }
}
```

### Rink Coordinate System

- Origin at center ice
- X-axis: lengthwise (-100 to 100 feet)
- Y-axis: widthwise (-42.5 to 42.5 feet)
- Rink dimensions: 200 x 85 feet
- Goal line: 89 feet from center (x = +/- 89)
- Blue line: 25 feet from center (x = +/- 25)
- Corner radius: 28 feet
- Teams switch ends each period (normalize in modeling)

### Game ID Format

Game IDs follow the pattern: `{season_start_year}{game_type}{game_number}`

- Season start year: 4 digits (e.g., `2024` for the 2024-2025 season)
- Game type: `01` = preseason, `02` = regular season, `03` = playoffs, `04` = all-star
- Game number: 4 digits (`0001` to `1312` for regular season with 32 teams)

Example: `2024020240` = 2024-25 season, regular season, game 240.

### Rate Limiting & Fetching Strategy

- No documented rate limits, but be respectful - add a small delay between requests (0.5-1s)
- A full regular season is ~1,312 games. Playoffs add ~80-100 more.
- Use the existing schedule/games data to get the list of `game_id` values to fetch
- Only fetch play-by-play for games with `gameState = "OFF"` (final) or `"LIVE"` (in progress)
- Once a game is final, its PBP data does not change - safe for incremental loading

---

## Ingestion Layer: dlt Pipeline

### Pipeline: `nhl_play_by_play_pipeline.py`

Create a dlt pipeline that produces two resources from the NHL Web API.

#### Resource 1: `play_by_play_events`

- Source: `/v1/gamecenter/{game-id}/play-by-play` -> flatten `plays` array
- Primary key: composite of `(game_id, event_id)`
- Write disposition: `merge` (upsert)
- Incremental strategy: use the existing games table to find `game_id` values not yet loaded. Track loaded games via a state variable or by checking what's already in the destination.
- Flatten the nested `plays` array. Each row = one event. Include: game_id, event_id, period number, period type, time_in_period, time_remaining, situation_code, type_code, type_desc_key, and all `details.*` fields (xCoord, yCoord, zoneCode, shootingPlayerId, goalieInNetId, shotType, etc.)
- Also extract `rosterSpots` into a separate child table or resource for game rosters

#### Resource 2: `boxscores`

- Source: `/v1/gamecenter/{game-id}/boxscore` -> flatten player stats
- Primary key: composite of `(game_id, player_id)`
- Write disposition: `merge`
- Flatten the nested `playerByGameStats` structure. Each row = one player-game. Include: game_id, player_id, team_id, position_group (forward/defense/goalie), sweater_number, toi, goals, assists, shots, hits, blocks, plus all other available stats.

#### Pipeline Configuration

```python
# Pipeline should be configurable for:
# - seasons to backfill (list of season strings like "20242025")
# - game types to include (default: [2, 3] for regular + playoffs)
# - whether to refetch live/recent games
```

#### Pydantic Models

Define Pydantic models for the API response structures to validate data on ingestion. At minimum:

- `PlayByPlayResponse` - top-level response
- `PlayEvent` - individual play event
- `EventDetails` - the `details` object (varies by event type)
- `RosterSpot` - player roster entry
- `BoxscoreResponse` - top-level boxscore
- `PlayerGameStats` - individual player stat line

Use discriminated unions or optional fields to handle the varying `details` structure across event types.

#### Client Design

Write a lightweight API client class for the NHL Web API. This should handle:

- Base URL configuration
- Rate limiting / sleep between requests
- Retry logic with backoff for transient failures
- Response validation against Pydantic models
- Logging

---

## dbt Model Layer

Follow the stg/int/mart layered approach. Entity is embedded in model names with the `nhl` prefix. Reference [dbt-agent-skills](https://github.com/dbt-labs/dbt-agent-skills) for dbt best practices.

### Staging Models

These do renaming, casting, deduplication, and light normalization. Source is the raw tables loaded by dlt.

#### `stg_nhl__play_by_play_events`

- Source: raw play-by-play events table from dlt
- Rename API fields to snake_case
- Cast types: game_id to integer, coordinates to float, times to interval/string as appropriate
- Deduplicate on (game_id, event_id)
- Normalize `type_desc_key` values (e.g., `"shot-on-goal"` -> `"shot_on_goal"`)
- Parse `situation_code` into discrete fields: `home_goalie_on_ice` (boolean), `home_skaters` (int), `away_skaters` (int), `away_goalie_on_ice` (boolean)
- Add `loaded_at` timestamp

#### `stg_nhl__boxscores`

- Source: raw boxscores table from dlt
- Rename and cast
- Parse TOI string ("18:42") into total seconds (integer) for easier aggregation
- Deduplicate on (game_id, player_id)

#### `stg_nhl__game_rosters`

- Source: raw roster spots from dlt
- One row per player per game with team_id, position, sweater_number

### Intermediate Models

This is where hockey analytics logic lives. These models enrich, filter, and derive new fields.

#### `int_nhl__events_enriched`

- Join `stg_nhl__play_by_play_events` with player and team dimension tables (from your existing models)
- Add `is_home_team_event` boolean
- Derive `strength_state` from `situation_code`:
  - `"5v5"`, `"5v4"` (power play), `"4v5"` (short-handed), `"4v4"`, `"3v3"`, `"5v3"`, `"3v5"`, `"empty_net"`, `"other"`
  - Account for pulled goalie (goalie_on_ice = 0) as empty net situations
- Normalize coordinates so the offensive zone is always positive X (adjust for period-based end switching)
- Add `game_seconds` - elapsed seconds from start of game (continuous clock across periods)

#### `int_nhl__shot_events`

- Filter `int_nhl__events_enriched` to shot attempt events only:
  - `shot_on_goal`, `goal`, `missed_shot`, `blocked_shot`
- Classify each event:
  - `is_corsi_event` = all four types above (CF/CA)
  - `is_fenwick_event` = all except blocked shots (FF/FA)
  - `is_shot_on_goal` = shots on goal + goals (SOG)
  - `is_goal` = goals only
- Calculate shot geometry from normalized coordinates:
  - `shot_distance` = distance from net (sqrt of (89 - abs(x))^2 + y^2)
  - `shot_angle` = angle to net center (atan2)
- Flag special shot types:
  - `is_rebound` = shot within 3 seconds of a prior shot attempt by either team
  - `is_rush_shot` = shot within 4 seconds of an event in another zone
- Carry forward: `shot_type` (wrist, slap, snap, backhand, tip-in, deflected, wrap-around)

#### `int_nhl__game_strength_states`

- From `int_nhl__events_enriched`, build a timeline of strength states per game
- Each row = a contiguous period of time at a given strength state within a game
- Fields: game_id, strength_state, period, start_game_seconds, end_game_seconds, duration_seconds
- This is used for time-weighted rate calculations (e.g., CF/60 at 5v5)

### Mart Models

Analytics-ready tables. These are the "answer" tables that serve dashboards, reports, or downstream analysis.

#### `fct_nhl__shot_attempts`

- Grain: one row per shot attempt event
- Core Corsi/Fenwick fact table
- Fields: game_id, event_id, player_id (shooter), team_id, opponent_team_id, period, game_seconds, strength_state, shot_type, shot_distance, shot_angle, x_coord, y_coord, is_corsi_event, is_fenwick_event, is_shot_on_goal, is_goal, is_rebound, is_rush_shot, is_home_event, zone_code

#### `fct_nhl__player_game_events`

- Grain: one row per event per player involvement
- All event types, not just shots
- Joins with boxscore for TOI context
- Fields: game_id, player_id, team_id, event_id, event_type, period, game_seconds, strength_state, plus event-specific details

#### `mart_nhl__player_on_ice_impact`

- Grain: one row per player per season (or per player-season-strength_state for splits)
- Aggregated on-ice metrics:
  - `cf` (Corsi For), `ca` (Corsi Against), `cf_pct` (CF%)
  - `ff` (Fenwick For), `fa` (Fenwick Against), `ff_pct` (FF%)
  - `sf` (Shots For), `sa` (Shots Against), `sf_pct`
  - `gf` (Goals For), `ga` (Goals Against), `gf_pct`
  - `cf_per_60`, `ca_per_60` (rate stats using time-on-ice)
- Requires joining shot attempts with game rosters to determine who was on ice
- Note: the play-by-play `situationCode` tells you the count of skaters, but not WHICH players were on ice. For full on-ice tracking, you would need shift data. Initial version can use the boxscore-level aggregation (player was in the game) rather than true on-ice. Add a TODO/note about this limitation. True on-ice impact requires shift-by-shift data as a future enhancement.

#### `mart_nhl__team_shot_quality`

- Grain: one row per team per season (or per game for game-level view)
- Shot location and quality metrics:
  - Shots by zone (inner slot, outer slot, point, perimeter)
  - High-danger chance count and percentage
  - Shooting percentage by zone
  - Shot distance distribution
- Zone classification logic (use normalized x/y coordinates):
  - Inner slot: abs(y) <= 9 and x >= 69 (within ~20 feet of net, narrow angle)
  - Outer slot: abs(y) <= 22 and x >= 54 (the "house")
  - Point: x >= 25 and x < 54 (between blue line and slot)
  - Perimeter: everything else in offensive zone
- These thresholds are approximations - document them and make them configurable via dbt vars

---

## Implementation Plan

### Sprint 1: Ingestion

1. Define Pydantic models for API responses
2. Build NHL API client with rate limiting and retry logic
3. Build dlt pipeline with `play_by_play_events` and `boxscores` resources
4. Test with a small sample (10-20 games)
5. Backfill current season

### Sprint 2: Staging + Intermediate

1. Create dbt sources for the raw dlt tables
2. Build staging models with tests (not_null, unique, accepted_values for event types)
3. Build `int_nhl__events_enriched` with coordinate normalization and strength state parsing
4. Build `int_nhl__shot_events` with distance/angle calculations and rebound/rush flags
5. Build `int_nhl__game_strength_states` timeline

### Sprint 3: Marts + Validation

1. Build `fct_nhl__shot_attempts` and `fct_nhl__player_game_events`
2. Build `mart_nhl__player_on_ice_impact` (game-level first, then season rollup)
3. Build `mart_nhl__team_shot_quality` with zone classification
4. Validate against known public stats (e.g., Natural Stat Trick, Hockey Reference) to sanity-check CF%, shot counts, etc.
5. Add dbt docs and descriptions

---

## dbt Testing Strategy

### Schema Tests

- `unique` + `not_null` on all primary keys
- `accepted_values` on `event_type` (known set of event types)
- `accepted_values` on `strength_state`
- `relationships` from events to games, players, teams (existing dims)
- `not_null` on coordinates for shot events specifically

### Data Tests (custom)

- Shot count per game should roughly match known box score totals
- Goals in play-by-play should match game final scores
- No events with `game_seconds` < 0 or > 4500 (max 75 min game with OT)
- Coordinate values within rink bounds: x in [-100, 100], y in [-43, 43]
- Every game should have at least one `period-start` and one `game-end` event

---

## Project File Structure

```
project-root/
|-- pipelines/
|   |-- nhl_play_by_play_pipeline.py    # dlt pipeline
|   |-- nhl_api_client.py               # API client class
|   |-- models/                         # Pydantic models
|   |   |-- __init__.py
|   |   |-- play_by_play.py
|   |   |-- boxscore.py
|-- dbt_project/
|   |-- models/
|   |   |-- staging/
|   |   |   |-- nhl/
|   |   |   |   |-- _nhl__sources.yml
|   |   |   |   |-- _nhl__models.yml
|   |   |   |   |-- stg_nhl__play_by_play_events.sql
|   |   |   |   |-- stg_nhl__boxscores.sql
|   |   |   |   |-- stg_nhl__game_rosters.sql
|   |   |-- intermediate/
|   |   |   |-- nhl/
|   |   |   |   |-- _nhl__models.yml
|   |   |   |   |-- int_nhl__events_enriched.sql
|   |   |   |   |-- int_nhl__shot_events.sql
|   |   |   |   |-- int_nhl__game_strength_states.sql
|   |   |-- marts/
|   |   |   |-- nhl/
|   |   |   |   |-- _nhl__models.yml
|   |   |   |   |-- fct_nhl__shot_attempts.sql
|   |   |   |   |-- fct_nhl__player_game_events.sql
|   |   |   |   |-- mart_nhl__player_on_ice_impact.sql
|   |   |   |   |-- mart_nhl__team_shot_quality.sql
```

---

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Ingestion tool | dlt | Already used in the project. Handles schema evolution, merge writes, and state management. |
| API client | Custom (httpx + tenacity) | NHL API is undocumented and needs flexible error handling. nhl-api-py is an option but adds a dependency for a small surface area. |
| Coordinate normalization | In dbt (intermediate layer) | Keeps raw data untouched in staging. Normalization logic is SQL-testable. |
| Strength state parsing | In dbt (staging) | Parse `situationCode` into discrete fields early so all downstream models benefit. |
| Shot zone classification | dbt vars | Thresholds for "inner slot", "outer slot" etc. are debatable. Making them configurable via `dbt_project.yml` vars lets you tune without code changes. |
| On-ice impact (initial) | Game-level, not shift-level | True on-ice requires shift data (future pipeline). Initial version uses "player was in the game" which is still useful for team-level and high-level player analysis. |

---

## Known Limitations & Future Work

- **On-ice attribution**: Without shift-by-shift data, `mart_nhl__player_on_ice_impact` attributes all team events to all players who played in the game. This overstates involvement. Shift data is the natural next pipeline to add.
- **Coordinate normalization**: Teams switch ends each period, but the API is inconsistent about which direction maps to which team. Validate by checking that most shot-on-goal events for the home team have positive x-coords in the first period (or whichever convention the API uses). Adjust normalization logic based on empirical observation.
- **Event coverage**: The NHL API is undocumented and may change. Event types, field names, and response structures can shift without notice. Build defensively with Pydantic validation and dbt accepted_values tests.
- **Historical data**: Play-by-play is available for recent seasons (approximately 2010+). Older seasons may have missing or inconsistent data. Start with current season and backfill intentionally.
- **xG model**: The shot events table (`fct_nhl__shot_attempts`) is designed to be the training dataset for an expected goals model. Fields like shot_distance, shot_angle, is_rebound, is_rush_shot, shot_type, and strength_state are the standard feature set. This is a natural next project once the pipeline is stable.

---

## Agent Instructions

When implementing this spec:

1. **Check for existing dlt and DuckDB agent skills** in your environment. If available, use them for pipeline and adapter patterns.
2. **Use dbt-agent-skills** (https://github.com/dbt-labs/dbt-agent-skills) for dbt model creation, testing, and documentation patterns.
3. **Match existing project conventions** - look at how the current player/team/game pipelines and models are structured and follow the same patterns for naming, configuration, and project layout.
4. **Build incrementally** - start with the dlt pipeline and staging models. Validate that data loads correctly before building intermediate and mart layers.
5. **Write typed Python** - all pipeline code should use type hints, Pydantic models, and docstrings. Lint with ruff.
6. **Test as you go** - add dbt tests alongside each model, not as a separate step at the end.
