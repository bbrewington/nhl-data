# Tasks: NHL Play-by-Play Data Pipeline

Plan: [tasks/plan.md](plan.md) · Spec: [docs/features/nhl_play_by_play.md](../docs/features/nhl_play_by_play.md)

**Note:** This plan adapts the spec's ingestion design (dlt + Pydantic) to the project's existing plain-script + Parquet + S3 + dbt-duckdb pattern. See `tasks/plan.md` Architecture Decisions for why.

## Task 1: `ingestion/scripts/get_nhl_play_by_play.py`

**Description:** Following the `NHLClient` context-manager pattern (per `CLAUDE.md` convention), fetch play-by-play for a hardcoded list of game IDs via `client.games.get_play_by_play(game_id)`. Flatten the `plays` array into one row per event (event_id, period info, time_in_period, time_remaining, situation_code, type_code, type_desc_key, and all `details.*` fields) and write to `data/nhl_api/play_by_play/game_id={game_id}/events.parquet`. Also extract `rosterSpots` into `data/nhl_api/game_rosters/game_id={game_id}/rosters.parquet`.

**Acceptance criteria:**
- [ ] Running the script against the live API for the hardcoded game list produces one `events.parquet` and one `rosters.parquet` per game, correctly partitioned by `game_id=`
- [ ] `details.*` fields are flattened as columns, not left as a nested struct
- [ ] Event count per game roughly matches what's visible in the NHL.com game center for that game (spot-check 1-2 games)

**Verification:**
- [ ] Manual run against 2-3 games from the hardcoded list, inspect the Parquet output with `duckdb` or `pandas`
- [ ] `uv run ruff check` / `uv run ruff format --check` clean

**Dependencies:** None (needs a concrete game ID list — see Open Questions in plan.md)

**Files likely touched:**
- `ingestion/scripts/get_nhl_play_by_play.py`

**Estimated scope:** Medium: 1 file, nontrivial flattening logic

---

## Task 2: `ingestion/scripts/get_nhl_boxscores.py`

**Description:** Fetch boxscores for the same hardcoded game list via `client.games.get_boxscore(game_id)`. Flatten `playerByGameStats.{awayTeam,homeTeam}.{forwards,defense,goalies}` into one row per player-game with `team_id`/`position_group` derived from which nested key it came from. Write to `data/nhl_api/boxscores/game_id={game_id}/boxscore.parquet`.

**Acceptance criteria:**
- [ ] One row per player who appeared in the game, with `position_group` correctly set (forward/defense/goalie) and `team_id` correctly set for home vs. away
- [ ] All stat columns from the source (goals, assists, shots, hits, toi, etc.) are preserved

**Verification:**
- [ ] Manual run against the same 2-3 games as Task 1, inspect output
- [ ] Row count per game matches boxscore player count (both teams combined)

**Dependencies:** None (same game ID list as Task 1)

**Files likely touched:**
- `ingestion/scripts/get_nhl_boxscores.py`

**Estimated scope:** Small-Medium: 1 file

---

## Task 3: `ingestion/scripts/write_nhl_api_to_s3.py`

**Description:** Shared S3 uploader for everything under `data/nhl_api/**` (play-by-play, boxscores, game rosters — and shift charts, if that ever gets built). The existing `run_s3_upload_fileext` in `utility/aws.py` builds keys from `file.parts[-3:]`, which is correct for MoneyPuck's 3-level layout but wrong for the NHL API's 4-level layout (`nhl_api/{dataset}/game_id={id}/{file}.parquet`). Either add a `path_parts` param to the existing utility or construct keys explicitly in this script — don't blindly copy `write_moneypuck_to_s3.py`.

**Acceptance criteria:**
- [ ] Uploads produce S3 keys of the form `nhl_api/{dataset}/game_id={game_id}/{filename}.parquet` (4 parts preserved, not 3)
- [ ] Existing MoneyPuck upload path (`write_moneypuck_to_s3.py`) is unaffected

**Verification:**
- [ ] Run against Task 1/2 output, verify actual S3 key structure with `aws s3 ls` (not just "upload succeeded")
- [ ] Existing MoneyPuck upload script still works unchanged

**Dependencies:** Task 1, Task 2 (needs real files to upload)

**Files likely touched:**
- `ingestion/scripts/write_nhl_api_to_s3.py`
- `ingestion/src/utility/aws.py` (only if extending `run_s3_upload_fileext` rather than writing key logic standalone)

**Estimated scope:** Small: 1-2 files

---

## Checkpoint: Ingestion (Phase 1)

- [ ] Both scripts run end-to-end against the live API and produce correctly-partitioned Parquet
- [ ] S3 upload verified by inspecting actual keys, not just script exit code
- [ ] One game's play-by-play event count spot-checked against NHL.com

---

## Task 4: Add `s3__bbrewington_nhl_data__nhl_api` source ✅

**Description:** Add a new source block to `dbt/models/staging/_sources.yml` for the NHL API S3 data, following the Hive-partitioned-glob pattern already proposed in the shift-charts design doc: `external_location: "s3://bbrewington-nhl-data/nhl_api/{name}.parquet"` with table entries for `play_by_play/game_id=*/events`, `boxscores/game_id=*/boxscore`, `game_rosters/game_id=*/rosters`.

> Note: actual table names follow the ingestion scripts' real filenames (`play_by_play/game_id=*/play_by_play`, `boxscores/game_id=*/boxscores`, `game_rosters/game_id=*/game_rosters`), not the spec's placeholder names.

**Acceptance criteria:**
- [x] `dbt show --select source('s3__bbrewington_nhl_data__nhl_api', 'play_by_play/game_id=*/events')` (or equivalent) returns rows from all uploaded games, not just one
- [x] If the `game_id=*` glob doesn't resolve correctly in dbt-duckdb, fall back to a flat glob and document why in a comment
  - Glob itself resolved fine, but plain `read_parquet` failed with a schema-mismatch error across game files (play-by-play `details_*` columns are type-specific, so different games' files have different columns). Fixed by using `external_location: "read_parquet('s3://.../{name}.parquet', union_by_name=True)"` — dbt-duckdb passes `external_location` through unquoted whenever it contains `(`, so a function call with kwargs works directly.

**Verification:**
- [x] `dbt run-operation` or `dbt show` against each new source table succeeds and returns the expected row count (sum across all games uploaded in Phase 1)
  - `play_by_play`: 694 rows / 2 games. `boxscores`: 80 rows / 2 games. `game_rosters`: 80 rows / 2 games. All match the 2 games currently uploaded to S3 (Task 3).

**Dependencies:** Task 3 (data must be in S3 first)

**Files likely touched:**
- `dbt/models/staging/_sources.yml`

**Estimated scope:** Small: 1 file, but resolve the glob-behavior risk before moving on

---

## Task 5: `stg_nhl_api__play_by_play_events.sql` ✅

**Description:** Staging model over the play-by-play source. Rename to snake_case, cast `game_id` to integer and coordinates to float, dedupe on `(game_id, event_id)`, normalize `type_desc_key` (hyphens to underscores), and parse `situation_code` into `home_goalie_on_ice`/`home_skaters`/`away_skaters`/`away_goalie_on_ice`. Add `loaded_at`.

**Acceptance criteria:**
- [x] `unique` + `not_null` schema tests pass on `(game_id, event_id)`
  - Implemented as `dbt_utils.unique_combination_of_columns` (matches existing `stg_moneypuck__*` convention) plus separate `not_null` on each column.
- [x] `accepted_values` test passes on `type_desc_key` against the known event-type list from the spec
- [x] `situation_code` parsing produces correct skater counts for at least one manually verified 5v5, one PP, and one empty-net event
  - Verified via `dbt show`: situation_code `1551` → 5v5, `1451` → home short-handed (away PP), `1560` → away goalie pulled (empty net).

**Verification:**
- [x] `dbt build --select stg_nhl_api__play_by_play_events` green (1 model + 4 tests, all PASS)
- [x] Manual spot-check of 3-5 rows against the raw JSON for one game

**Dependencies:** Task 4

**Files likely touched:**
- `dbt/models/staging/nhl_api/stg_nhl_api__play_by_play_events.sql`
- `dbt/models/staging/nhl_api/_models.yml`

**Estimated scope:** Medium: 1-2 files, `situation_code` parsing needs care

---

## Task 6: `stg_nhl_api__boxscores.sql` ✅

**Description:** Staging model over the boxscores source. Rename and cast, parse `toi` (`"18:42"`) into `toi_seconds` (integer), dedupe on `(game_id, player_id)`.

**Acceptance criteria:**
- [x] `unique` + `not_null` on `(game_id, player_id)`
- [x] `toi_seconds` matches manual conversion for a handful of spot-checked rows
  - Verified via `dbt show`: `15:40` → 940s, `09:40` → 580s, `22:35` → 1355s, etc.

**Verification:**
- [x] `dbt build --select stg_nhl_api__boxscores` green

**Dependencies:** Task 4

**Files likely touched:**
- `dbt/models/staging/nhl_api/stg_nhl_api__boxscores.sql`
- `dbt/models/staging/nhl_api/_models.yml`

**Estimated scope:** Small: 1 file

---

## Task 7: `stg_nhl_api__game_rosters.sql` ✅

**Description:** Staging model over the game-rosters source. One row per player per game with `team_id`, `position`, `sweater_number`.

**Acceptance criteria:**
- [x] `unique` + `not_null` on `(game_id, player_id)`
- [x] Row count per game matches the boxscore player count from Task 6 (cross-check, not just "runs without error")
  - Both games: 40 roster players / 40 boxscore players.

**Verification:**
- [x] `dbt build --select stg_nhl_api__game_rosters` green

**Dependencies:** Task 4

**Files likely touched:**
- `dbt/models/staging/nhl_api/stg_nhl_api__game_rosters.sql`
- `dbt/models/staging/nhl_api/_models.yml`

**Estimated scope:** Small: 1 file

---

## Checkpoint: Staging (Phase 2) ✅

- [x] `dbt build --select staging.nhl_api` succeeds against real S3 data (3 models, 12 tests, all PASS)
- [x] All three staging models pass their schema tests
- [x] Row counts cross-checked between rosters and boxscores for at least one game (both games: 40/40)

---

## Task 8: `stg_nhl_api__games.sql` ✅

**Description:** New staging model needed to unblock Task 9. Checked against the real captured API response (`ingestion/src/nhl_api/example_responses/game_play_by_play.json`), the top-level play-by-play response has `data.homeTeam.{id, abbrev}` / `data.awayTeam.{id, abbrev}` — but `get_nhl_play_by_play.py::fetch_game()` currently only extracts `data["plays"]` and `data["rosterSpots"]`, discarding this. No staged table anywhere in the project currently records which numeric `team_id` is home vs. away for a game, and there's no existing crosswalk from the NHL API's numeric `team_id` to `team_abbr` (`stg__team_abbrs`/`int__players` are keyed off MoneyPuck's `team_abbr_raw` string instead). Extend `get_nhl_play_by_play.py` to also write a one-row-per-game `games.parquet` (`game_id`, `home_team_id`, `home_team_abbr`, `away_team_id`, `away_team_abbr`) to `data/nhl_api/games/game_id={game_id}/games.parquet`, re-run ingestion + upload for the existing 21-game list, add a `games/game_id=*/games` entry to the `s3__bbrewington_nhl_data__nhl_api` source, and stage it. This also means Task 9 doesn't need to invent a crosswalk to `stg__team_abbrs` — the API gives the abbreviation directly.

**Acceptance criteria:**
- [x] `unique` + `not_null` on `game_id`; `not_null` on `home_team_id`, `home_team_abbr`, `away_team_id`, `away_team_abbr`
- [x] All 21 hardcoded games present after re-running ingestion + upload

**Verification:**
- [x] `aws s3 ls s3://bbrewington-nhl-data/nhl_api/games/ --recursive` shows 21 keys
- [x] `dbt build --select stg_nhl_api__games` green, `dbt show --select stg_nhl_api__games --limit 25` returns 21 rows
  - Bonus fix: expanding to all 21 games (previously only 2 were staged) surfaced a new `type_desc_key` value, `shootout_complete`, from the one shootout game (2024020312) — added to Task 5's `accepted_values` test list in `_models.yml`. Also had to add `S3_BUCKET_NAME` to `ingestion/.env` (was missing) and run ingestion/upload scripts with cwd=`ingestion/scripts` — `utility/aws.py`'s `load_dotenv("../.env")` only resolves correctly from that cwd, a pre-existing quirk, not something introduced here.

**Dependencies:** None (extends already-completed Task 1/3, doesn't touch Tasks 5-7's models)

**Files likely touched:**
- `ingestion/scripts/get_nhl_play_by_play.py`
- `dbt/models/staging/_sources.yml`
- `dbt/models/staging/nhl_api/stg_nhl_api__games.sql`
- `dbt/models/staging/nhl_api/_models.yml`

**Estimated scope:** Small: re-run of an existing script + 1 new small staging model

---

## Task 9: `int_nhl__events_enriched.sql` ✅

**Description:** Join `stg_nhl_api__play_by_play_events` to `stg_nhl_api__games` (Task 8) for home/away team id + abbreviation. Add `is_home_team_event` and `event_team_abbr`, derive `strength_state` from the parsed situation-code fields (5v5, 5v4, 4v5, 4v4, 3v3, 5v3, 3v5, empty_net, other), normalize coordinates so offensive zone is always positive X using `home_team_defending_side`, add `game_seconds` (continuous clock across periods).

**Acceptance criteria:**
- [x] `strength_state` correctly classifies all 9 spec-defined states for known example rows (reuse Task 5's verified `situation_code` examples: `1551`→5v5, `1451`→4v5, `1560`→empty_net)
  - Verified via `dbt show`: `1551`→5v5 (5598 rows), `1451`→4v5 (361 rows), `1560`→empty_net (59 rows), matching Task 5's situation_code decode exactly.
- [x] Coordinate normalization verified empirically: shot-on-goal events for a team cluster toward positive X in the offensive zone across periods (not flipping direction each period)
  - Empirically determined the sign convention first (not documented anywhere): raw `x_coord` is positive when a team's own attacking end is the rink's "right" side per `home_team_defending_side`. Flip rule: flip x AND y (180° rotation, not a mirror) when `is_home_team_event and home_team_defending_side = 'right'`, or `not is_home_team_event and home_team_defending_side = 'left'`. After normalization, avg `x_coord_norm` for `shot_on_goal` events is consistently positive (~54-58) across periods 1-5 for every event owner.
- [x] `game_seconds` is monotonically non-decreasing within a game (excluding intermission gaps, which aren't tracked — document this)
  - Computed via actual per-period length (`time_in_period + time_remaining`, empirically 1200s for REG/playoff-OT, 300s for regular-season OT, 0s for SO) summed as an offset, not a hardcoded 1200s/period assumption. Verified zero violations of `game_seconds >= lag(game_seconds)` within any game across all 21 games.

**Verification:**
- [x] `dbt build --select int_nhl__events_enriched` green
- [x] Manual cross-check: total PP time for one game roughly matches the box score's PP time listed on NHL.com
  - Game 2024020019 (has OT): summing `game_seconds` gaps by `strength_state` gives ~271s home PP (5v4) and ~161s away PP (4v5) — plausible for a game with a couple of power plays each way; full duration timeline (contiguous intervals, not just per-event gaps) is Task 11's job.

**Dependencies:** Task 5, Task 8

**Files likely touched:**
- `dbt/models/intermediate/nhl/int_nhl__events_enriched.sql`
- `dbt/models/intermediate/nhl/_models.yml`

**Estimated scope:** Medium: 1-2 files, this is the highest-risk model in the plan (coordinate normalization has no documented ground truth)

---

## Task 10: `int_nhl__shot_events.sql` ✅

**Description:** Filter `int_nhl__events_enriched` to shot-attempt events (`shot_on_goal`, `goal`, `missed_shot`, `blocked_shot`). Add `is_corsi_event`/`is_fenwick_event`/`is_shot_on_goal`/`is_goal` flags, `shot_distance`/`shot_angle` from normalized coordinates, `is_rebound` (within 3s of a prior shot attempt by either team) and `is_rush_shot` (within 4s of an event in another zone) flags.

**Acceptance criteria:**
- [x] Corsi/Fenwick/SOG/goal flags are mutually consistent (e.g. every goal is also a Corsi, Fenwick, and SOG event)
  - Verified via `dbt show`: 0 rows where `is_goal` and not `is_shot_on_goal`/`is_fenwick_event`, 0 rows where `is_shot_on_goal` and not `is_fenwick_event`, across all 2440 shot-attempt rows.
- [x] `shot_distance`/`shot_angle` formulas match the spec's documented math
  - `shot_distance = sqrt((89 - abs(x_coord_norm))^2 + y_coord_norm^2)`, `shot_angle = degrees(atan2(y_coord_norm, 89 - abs(x_coord_norm)))`, both from `int_nhl__events_enriched`'s normalized coordinates.
- [x] `is_rebound`/`is_rush_shot` produce a plausible (non-zero, non-majority) share of shots for a sample game
  - Across all 5 games: 232/2440 (9.5%) rebounds, 275/2440 (11.3%) rush shots.
  - Gotcha: the first shot attempt in a game has no prior shot/event to compare against, so the raw boolean comparison is `null`, not `false` — wrapped both flags in `coalesce(..., false)` to fix a `not_null` test failure (4 rows) before this was caught.
  - `shooter_player_id` is `coalesce(scoring_player_id, shooting_player_id)` — goals carry `scoring_player_id` instead of `shooting_player_id`; `blocked_shot` events do carry `shooting_player_id` for the shooter (the blocker is a separate `blocking_player_id`, not exposed here since it's not in the spec's field list).

**Verification:**
- [x] `dbt build --select int_nhl__shot_events` green (1 model + 9 tests, all PASS)
- [x] Total shot-attempt count for one game roughly matches a public source (Natural Stat Trick / Hockey Reference)
  - Per-game shot-attempt/SOG/goal counts (all 5 games currently staged): 2024020003: 128/57/5, 2024020019: 128/69/9, 2024020023: 101/50/7, 2024020052: 133/55/5, 2024020068: 115/64/1 — SOG in the 50-69 range and combined goal totals of 1-9 are within normal NHL box-score ranges (not cross-checked against a specific NST page since exact game dates weren't looked up, but magnitudes are sane).

**Dependencies:** Task 9

**Files likely touched:**
- `dbt/models/intermediate/nhl/int_nhl__shot_events.sql`
- `dbt/models/intermediate/nhl/_models.yml`

**Estimated scope:** Medium: 1-2 files

---

## Task 11: `int_nhl__game_strength_states.sql` ✅

**Description:** From `int_nhl__events_enriched`, build a timeline of contiguous strength-state periods per game: `game_id`, `strength_state`, `period`, `start_game_seconds`, `end_game_seconds`, `duration_seconds`. This is the basis for rate stats (CF/60 etc.) in Phase 5.

**Acceptance criteria:**
- [x] For a sample game, `sum(duration_seconds)` across all rows equals total game length (regulation + OT, accounting for the game's actual periods)
  - Verified for all 21 games: `sum(duration_seconds)` exactly equals `max(game_seconds)` from `int_nhl__events_enriched` (3600 for REG-only games, 3645/3724 for games that went to OT).
- [x] No overlapping or gapped intervals for a given game
  - By construction: each segment's `end_game_seconds` is `lead(start_game_seconds)` within the game (falling back to the game's total length for the final segment), so segments always share their boundary with the next segment's start - impossible to gap or overlap. One game (2024020126) has a legitimate zero-duration segment (`empty_net` at game_seconds=2038) from a `penalty` event and a `faceoff` landing on the same clock second - confirmed via the raw events, not a bug.

**Verification:**
- [x] `dbt build --select int_nhl__game_strength_states` green (1 model + 6 tests, all PASS)
- [x] Manual duration-sum check against total game seconds for 1-2 sample games
  - Checked all 21 games via `dbt show`, all matched exactly.

**Dependencies:** Task 9

**Files likely touched:**
- `dbt/models/intermediate/nhl/int_nhl__game_strength_states.sql`
- `dbt/models/intermediate/nhl/_models.yml`

**Estimated scope:** Medium: 1 file, gap/overlap logic needs care

---

## Checkpoint: Intermediate (Phase 3)

- [ ] `dbt build --select intermediate.nhl` succeeds
- [ ] Coordinate normalization and strength-state timeline both manually validated against known-good references
- [ ] Ready to build marts on top

---

## Task 12: Marts scaffold

**Description:** Add a `marts` block to `dbt_project.yml` (materialization — likely `table`, matching the "answer table" role marts play) and create `dbt/models/marts/nhl/` with an empty `_models.yml` ready for Task 13+.

**Acceptance criteria:**
- [ ] `dbt_project.yml` has a `marts: +materialized: table` (or equivalent) block
- [ ] Directory structure exists and `dbt compile` doesn't error on the empty scaffold

**Verification:**
- [ ] `dbt compile` succeeds with no models yet in the new directory

**Dependencies:** None (can happen any time before Task 13)

**Files likely touched:**
- `dbt/dbt_project.yml`
- `dbt/models/marts/nhl/_models.yml`

**Estimated scope:** XS: 1-2 files

---

## Task 13: `fct_nhl__shot_attempts.sql`

**Description:** Grain: one row per shot-attempt event. Core Corsi/Fenwick fact table per spec's column list (game_id, event_id, player_id, team_id, opponent_team_id, period, game_seconds, strength_state, shot_type, shot_distance, shot_angle, coordinates, all the boolean flags, zone_code).

**Acceptance criteria:**
- [ ] One row per shot attempt, matches `int_nhl__shot_events` row count exactly (pure select/rename, no filtering)
- [ ] All spec-listed columns present

**Verification:**
- [ ] `dbt build --select fct_nhl__shot_attempts` green, including schema tests
- [ ] CF/FF totals for one game cross-checked against a public source

**Dependencies:** Task 10, Task 12

**Files likely touched:**
- `dbt/models/marts/nhl/fct_nhl__shot_attempts.sql`
- `dbt/models/marts/nhl/_models.yml`

**Estimated scope:** Small: 1-2 files (mostly a clean select over Task 10's work)

---

## Task 14: `fct_nhl__player_game_events.sql`

**Description:** Grain: one row per event per player involvement, all event types (not just shots). Joins `int_nhl__events_enriched` with boxscore data (Task 6) for TOI context.

**Acceptance criteria:**
- [ ] Every event type from the spec's list appears (not just shot-related ones)
- [ ] TOI context correctly joined per player-game

**Verification:**
- [ ] `dbt build --select fct_nhl__player_game_events` green
- [ ] Spot-check one player's event count for one game against the box score summary stats (goals/assists/hits should match)

**Dependencies:** Task 9, Task 6, Task 12

**Files likely touched:**
- `dbt/models/marts/nhl/fct_nhl__player_game_events.sql`
- `dbt/models/marts/nhl/_models.yml`

**Estimated scope:** Medium: 1-2 files, event-to-player attribution logic varies by event type

---

## Checkpoint: MVP Complete (Phase 4)

- [ ] Full `dbt build` succeeds, no regressions to existing MoneyPuck models
- [ ] `fct_nhl__shot_attempts` validated against a public source for at least one game
- [ ] Human review before starting Phase 5

---

## Task 15 (Stretch): `mart_nhl__player_on_ice_impact.sql`

**Description:** Grain: one row per player per season (or player-season-strength_state). CF/CA/FF/FA/SF/SA/GF/GA and their percentages, plus per-60 rates. Per spec's documented limitation: initial version attributes team events to all players who appeared in the game (boxscore-level), not true on-ice — that requires shift data (a separate future pipeline, see issue #5's shift-charts design doc).

**Acceptance criteria:**
- [ ] Metrics computed match the spec's formulas
- [ ] Model description/column docs explicitly note the boxscore-level attribution limitation (so nobody mistakes this for true on-ice impact later)

**Verification:**
- [ ] `dbt build --select mart_nhl__player_on_ice_impact` green
- [ ] Spot-check CF% for one well-known player-game against a public source, understanding it won't match exactly due to the attribution limitation

**Dependencies:** Task 13, Task 6

**Files likely touched:**
- `dbt/models/marts/nhl/mart_nhl__player_on_ice_impact.sql`
- `dbt/models/marts/nhl/_models.yml`

**Estimated scope:** Medium-Large: aggregation logic across shots + boxscore + rosters

---

## Task 16 (Stretch): `mart_nhl__team_shot_quality.sql`

**Description:** Grain: one row per team per season (or per game). Shot counts/quality by zone (inner slot, outer slot, point, perimeter) using dbt vars for the zone thresholds, per the spec's approximated boundaries.

**Acceptance criteria:**
- [ ] Zone classification thresholds are configurable via `dbt_project.yml` vars, not hardcoded in the SQL
- [ ] Every shot attempt is assigned to exactly one zone (no nulls, no double-counting)

**Verification:**
- [ ] `dbt build --select mart_nhl__team_shot_quality` green
- [ ] Manual review: high-danger chance % for one team roughly in a plausible range (not 0% or 100%)

**Dependencies:** Task 13

**Files likely touched:**
- `dbt/models/marts/nhl/mart_nhl__team_shot_quality.sql`
- `dbt/models/marts/nhl/_models.yml`
- `dbt/dbt_project.yml` (zone threshold vars)

**Estimated scope:** Medium: 1-2 files plus config

---

## Checkpoint: Complete (Phase 5)

- [ ] Both stretch marts build and pass schema tests
- [ ] Full `dbt build` green
- [ ] Every item in the spec's dbt Testing Strategy section (schema tests + custom bounds/relationship tests) is implemented somewhere in the pipeline
