# NHL API Shift Charts — Design Spec

**Date:** 2026-03-23
**Branch:** `add-nhl-api-shifts` (cut from `main`)

## Goal

Ingest NHL shift chart data for a small set of games and build dbt staging + intermediate models to support three analytics use cases:
- (a) Line combinations — who plays with whom
- (b) Ice time by period per player
- (c) Shift length / fatigue patterns

Situation-level ice time (PP/PK/5v5) is a known gap; the schema includes a `situation` placeholder column to be filled in later when play-by-play data is added.

## Scope

- 2 games from the same team (hardcoded game IDs for initial validation)
- Ingestion → S3 → dbt staging + intermediate only (no mart layer yet)

---

## Section 1: Ingestion

### `ingestion/scripts/get_nhl_shift_charts.py`

- Hardcoded list of 2 game IDs
- Uses `NHLClient` as a context manager: `with NHLClient() as client:` (per project convention)
- Calls `client.games.get_shift_charts(game_id)` for each game
- **Response structure:** The live API returns `{"data": [...]}` — access shift rows via `response["data"]`. Do not use `game_shift_charts.json` to infer the access path; that example file has an additional metadata wrapper added by the project's response collector and does not reflect what `_get` returns at runtime.
- **Filter:** Keep only actual shift rows — drop rows where `playerId` is null (the API response includes period-marker event rows alongside shift rows)
- Saves as Parquet to:
  ```
  data/nhl_api/shift_charts/game_id={game_id}/shifts.parquet
  ```

### `ingestion/scripts/write_nhl_api_to_s3.py`

- Uploads everything under `data/nhl_api/` to S3 at:
  ```
  s3://bbrewington-nhl-data/nhl_api/shift_charts/game_id={game_id}/shifts.parquet
  ```
- The `game_id=` directory partitioning allows dbt to glob all games
- **Note on S3 key construction:** The existing `run_s3_upload_fileext` utility uses `file.parts[-3:]` to build S3 keys — correct for MoneyPuck's 3-level layout but wrong for the 4-level NHL API layout (`nhl_api/shift_charts/game_id={game_id}/shifts.parquet`). This script must use `file.parts[-4:]` or construct keys explicitly. Do not blindly mirror `write_moneypuck_to_s3.py`.

---

## Section 2: dbt Staging

### New source in `dbt/models/staging/_sources.yml`

**Primary approach** (Hive-partitioned glob):
```yaml
- name: s3__bbrewington_nhl_data__nhl_api
  meta:
    external_location: "s3://bbrewington-nhl-data/nhl_api/{name}.parquet"
  tables:
    - name: shift_charts/game_id=*/shifts
```
This expands to `s3://bbrewington-nhl-data/nhl_api/shift_charts/game_id=*/shifts.parquet`. Validate that dbt-duckdb handles the `=` and `*` in the path correctly.

**Fallback** (if Hive glob fails): Flatten the S3 path to `shift_charts/*.parquet` (one file per game, named by game_id) and change the source entry to:
```yaml
  tables:
    - name: shift_charts/*
```

### `dbt/models/staging/nhl_api/stg_nhl_api__shifts.sql`

Transformations:
- Rename columns to snake_case (`gameId` → `game_id`, `playerId` → `player_id`, `teamAbbrev` → `team_abbr_raw`, etc.)
- **Normalize team abbreviations:** join to `{{ ref('stg__team_abbrs') }}` on `team_abbr_raw` to produce a canonical `team_abbr` (per project convention — handles variants like `"S.J"` → `"SJS"`)
- Convert `startTime` / `endTime` (strings `"MM:SS"`) to integer seconds for `shift_start_seconds` and `shift_end_seconds`
- **Use source `duration` field** for `duration_seconds`: convert the `duration` column (`"MM:SS"` string) directly to integer seconds rather than deriving from end minus start (the source field is authoritative and handles edge cases like period-end truncation)
- Output columns: `game_id`, `player_id`, `team_abbr`, `period`, `shift_number`, `first_name`, `last_name`, `shift_start_seconds`, `shift_end_seconds`, `duration_seconds`, `situation`
- Add: `situation` as `null` — placeholder for future play-by-play enrichment

Materialization: `table` (consistent with other staging models)

---

## Section 3: dbt Intermediate

### `dbt/models/intermediate/int__player_shifts.sql`

One row per player per shift. Adds player dimension enrichment over the staging model via join to `{{ ref('int__players') }}`.

**Join key:** `stg_nhl_api__shifts.player_id = int__players.mp_player_id` — these are the same identifier (NHL API player ID); MoneyPuck sources it under the name `mp_player_id`.

Adds from `int__players`: `mp_player_name` (alias as `player_full_name` in output), `position` (and any other available player attributes).

Key output columns: `game_id`, `player_id`, `player_full_name`, `position`, `team_abbr`, `period`, `shift_number`, `shift_start_seconds`, `shift_end_seconds`, `duration_seconds`, `situation`

Supports:
- Ice time per player per game/period (goal b) — aggregate `duration_seconds` grouped by `player_id`, `game_id`, `period`
- Shift length distribution per player (goal c) — `duration_seconds` per row

Materialization: `view`

### `dbt/models/intermediate/int__line_combinations.sql`

Self-join on `int__player_shifts` to find overlapping shifts between same-team players in the same game and period.

Logic:
- Join player A shifts to player B shifts: same `game_id`, `team_abbr`, and `period`; `player_id_1 < player_id_2` (avoid duplicate pairs)
- Overlap condition: `a.shift_start_seconds < b.shift_end_seconds AND b.shift_start_seconds < a.shift_end_seconds`
- `shared_ice_time_seconds = least(a.shift_end_seconds, b.shift_end_seconds) - greatest(a.shift_start_seconds, b.shift_start_seconds)`
- **Aggregate across all periods:** final GROUP BY is `game_id, team_abbr, player_id_1, player_id_2` — `period` is intentionally dropped to give a game-level line combination total. Period-level breakdown is not in scope for this phase.

Output columns: `game_id`, `team_abbr`, `player_id_1`, `player_id_2`, `shared_ice_time_seconds`

Supports goal (a) — line combinations.

Materialization: `view`

---

## Known Gaps / Future Work

- `situation` (PP/PK/5v5) requires cross-referencing with play-by-play data — out of scope for this phase
- Only 2 games loaded initially; scaling to full season is a follow-up
- No mart layer yet — `int__player_shifts` and `int__line_combinations` are the query surface for now
- Period-level line combination breakdowns deferred to a future iteration
