# Implementation Plan: NHL Play-by-Play Data Pipeline

Spec: [docs/features/nhl_play_by_play.md](../docs/features/nhl_play_by_play.md)

## Overview

Ingest NHL play-by-play events, boxscores, and game rosters from the NHL Web API, and build dbt staging/intermediate/mart models on top for shot analysis (Corsi/Fenwick), player-game events, and on-ice impact. This is the same class of dataset as the existing MoneyPuck shots data, but sourced independently from the NHL API's raw event stream, which unlocks situational (strength-state) analysis MoneyPuck doesn't expose directly.

## Architecture Decisions

- **No dlt, no Pydantic, no `pipelines/` directory.** The spec's Ingestion Layer section (lines 121-175) describes a dlt-based pipeline that doesn't match this project's actual conventions — there is no `dlt` dependency anywhere in `ingestion/`, and every existing NHL API script (`get_nhl_api_data.py`, and the shift-charts design doc) uses the plain `NHLClient` resource pattern: fetch JSON → flatten to a DataFrame → write Parquet → upload to S3 → let dbt-duckdb read the S3 Parquet as an external source. This plan follows that existing pattern instead, confirmed with the user.
- **Small hardcoded game list for initial validation, not a season backfill.** Mirrors the precedent set by the shift-charts design doc (2 hardcoded games). This plan uses roughly 10-20 games from one team's early season for validation — enough to exercise shot events, strength-state transitions, and boxscore joins without dealing with incremental-loading/state-tracking machinery. Full-season backfill and true incremental loading (only fetching new/final games) are explicitly deferred — see Open Questions.
- **New dbt source `s3__bbrewington_nhl_data__nhl_api`**, following the same Hive-partitioned-glob approach proposed in the shift-charts design doc (`nhl_api/{play_by_play,boxscores,game_rosters}/game_id=*/*.parquet`). If dbt-duckdb chokes on the `game_id=*` glob, fall back to a flat `game_id` column embedded in the filename instead of the directory (same fallback the shift-charts doc already documents).
- **A shared `write_nhl_api_to_s3.py` uploader is a new dependency of this work.** It doesn't exist yet (the shift-charts doc specified one but it was never built). The existing `run_s3_upload_fileext` utility assumes MoneyPuck's 3-level path layout (`file.parts[-3:]`); NHL API data is 4 levels deep (`nhl_api/{dataset}/game_id={id}/{file}.parquet`), so this needs `file.parts[-4:]` or explicit key construction — call this out explicitly since it's an easy off-by-one.
- **Mart layer is new.** `dbt_project.yml` currently only configures `staging` (table) and `intermediate` (view) materializations — there is no `marts` config or `models/marts/` directory yet. Phase 4 adds both.
- **Marts split into MVP vs. stretch.** `fct_nhl__shot_attempts` and `fct_nhl__player_game_events` are the core deliverables (Phase 4). `mart_nhl__player_on_ice_impact` and `mart_nhl__team_shot_quality` are more open-ended aggregations with configurable thresholds (Phase 5) — scoped separately so Phase 4 can ship and be reviewed on its own.
- **xG model and shift-based on-ice attribution are out of scope**, per the spec's own "Out of Scope" section — not revisited here.

## Task List

### Phase 1: Ingestion

- [x] Task 1: `ingestion/scripts/get_nhl_play_by_play.py` — fetch play-by-play + rosters for a hardcoded game list
- [x] Task 2: `ingestion/scripts/get_nhl_boxscores.py` — fetch boxscores for the same game list
- [ ] Task 3: `ingestion/scripts/write_nhl_api_to_s3.py` — shared uploader for all `data/nhl_api/**` output

### Checkpoint: Ingestion
- [x] `get_nhl_play_by_play.py` and `get_nhl_boxscores.py` run end-to-end against the live API for the hardcoded game list and produce Parquet files with the expected partitioning (`data/nhl_api/{play_by_play,boxscores,game_rosters}/game_id={id}/*.parquet`)
- [ ] `write_nhl_api_to_s3.py` uploads to the correct S3 keys (verify key structure, not just that *a* key was written)
- [x] Spot-check one game's play-by-play row count against the NHL.com boxscore for that game — game 2024020003 (STL @ SEA): 52 shot-on-goal + 5 goal events = 57, matches API's reported `awayTeam.sog` (25) + `homeTeam.sog` (32) = 57
- [x] Spot-check `get_nhl_boxscores.py` output for the same game — summing `sog` by `team_id` gives 25/32, matching the play-by-play cross-check above; 40 player rows (20 forwards, 12 defense, 4 goalies split evenly across the two teams)

### Phase 2: dbt Staging

- [ ] Task 4: Add `s3__bbrewington_nhl_data__nhl_api` source to `dbt/models/staging/_sources.yml`
- [ ] Task 5: `dbt/models/staging/nhl_api/stg_nhl_api__play_by_play_events.sql`
- [ ] Task 6: `dbt/models/staging/nhl_api/stg_nhl_api__boxscores.sql`
- [ ] Task 7: `dbt/models/staging/nhl_api/stg_nhl_api__game_rosters.sql`

### Checkpoint: Staging
- [ ] `dbt build --select staging.nhl_api` succeeds against real S3 data
- [ ] `not_null`/`unique`/`accepted_values` schema tests pass for all three staging models
- [ ] Row counts are sane (staging row count == raw Parquet row count, no silent drops from joins)

### Phase 3: dbt Intermediate

- [ ] Task 8: `dbt/models/intermediate/nhl/int_nhl__events_enriched.sql`
- [ ] Task 9: `dbt/models/intermediate/nhl/int_nhl__shot_events.sql`
- [ ] Task 10: `dbt/models/intermediate/nhl/int_nhl__game_strength_states.sql`

### Checkpoint: Intermediate
- [ ] `dbt build --select intermediate.nhl` succeeds
- [ ] Coordinate normalization validated empirically (see spec's "Known Limitations" note on end-switching) against 2-3 known shot locations
- [ ] Strength-state timeline for one game manually cross-checked against the live broadcast/box score (e.g. PP time roughly matches)

### Phase 4: dbt Marts (MVP)

- [ ] Task 11: Add `marts` materialization config to `dbt_project.yml`, create `dbt/models/marts/nhl/` scaffold
- [ ] Task 12: `dbt/models/marts/nhl/fct_nhl__shot_attempts.sql`
- [ ] Task 13: `dbt/models/marts/nhl/fct_nhl__player_game_events.sql`

### Checkpoint: MVP Complete
- [ ] `dbt build` (full project) succeeds with no regressions to existing MoneyPuck models
- [ ] `fct_nhl__shot_attempts` CF/FF counts for one game roughly match a public source (e.g. Natural Stat Trick) for that game
- [ ] Ready for human review before starting Phase 5

### Phase 5: dbt Marts (Stretch — separate review checkpoint)

- [ ] Task 14: `dbt/models/marts/nhl/mart_nhl__player_on_ice_impact.sql` (game-level boxscore-based attribution, per spec's documented limitation)
- [ ] Task 15: `dbt/models/marts/nhl/mart_nhl__team_shot_quality.sql` with zone-classification thresholds as dbt vars

### Checkpoint: Complete
- [ ] All Phase 5 marts build and pass schema tests
- [ ] `dbt build` full project green
- [ ] Every item in the spec's dbt Testing Strategy section is implemented somewhere (schema tests + at least the row-count/bounds custom tests)

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec assumes dlt/Pydantic ingestion; adapting to plain-script pattern means losing schema validation on ingest | Med | Rely on dbt schema tests (accepted_values, not_null, bounds checks) as the validation layer instead — same approach already used for MoneyPuck data |
| `game_id=*` Hive-partitioned glob may not work cleanly in dbt-duckdb (unconfirmed — same open risk flagged in the shift-charts doc) | Med | Task 4 validates this first, before staging models are built on top; fallback is a flat `shift_charts/*` style glob |
| Coordinate normalization (which end each team shoots at, per period) is empirically determined, not documented by the API | High | Task 8 validates against known shot-on-goal patterns before downstream models depend on it; get this right early since everything in Phase 3+ depends on it |
| NHL API is undocumented and unversioned — response shape could differ from the captured example (`game_play_by_play.json`) | Low-Med | Staging models should fail loudly (dbt tests) rather than silently coercing on shape mismatches |
| Small hardcoded game list may not exercise all `situationCode` / event-type edge cases (e.g. shootouts, 3-on-3 OT) | Med | Deliberately pick games spanning regulation, OT, and if possible a shootout when choosing the initial game list in Task 1 |

## Resolved Decisions

- **Hardcoded game list (Task 1 input):** STL (St. Louis Blues), 2024-2025 regular season, chosen because `team_schedule_stl.json` is already a captured example fixture in `ingestion/src/nhl_api/example_responses/`, consistent with existing `client.teams.get_schedule("STL")` usage in `get_nhl_api_data.py`. 21 games spanning Oct 8 - Nov 21, 2024 — 16 regulation, 4 OT, 1 shootout (for `situationCode`/game-state edge case coverage):

  ```
  2024020003  2024-10-08  STL @ SEA   REG
  2024020019  2024-10-10  STL @ SJS   OT
  2024020023  2024-10-11  STL @ VGK   REG
  2024020052  2024-10-15  MIN @ STL   REG
  2024020068  2024-10-17  NYI @ STL   OT
  2024020084  2024-10-19  CAR @ STL   REG
  2024020099  2024-10-22  WPG @ STL   REG
  2024020110  2024-10-24  STL @ TOR   REG
  2024020126  2024-10-26  STL @ MTL   REG
  2024020150  2024-10-29  STL @ OTT   REG
  2024020162  2024-10-31  STL @ PHI   REG
  2024020181  2024-11-02  TOR @ STL   REG
  2024020199  2024-11-05  TBL @ STL   REG
  2024020215  2024-11-07  UTA @ STL   REG
  2024020229  2024-11-09  WSH @ STL   REG
  2024020248  2024-11-12  BOS @ STL   REG
  2024020257  2024-11-14  STL @ BUF   OT
  2024020272  2024-11-16  STL @ BOS   OT
  2024020284  2024-11-17  STL @ CAR   REG
  2024020296  2024-11-19  MIN @ STL   REG
  2024020312  2024-11-21  SJS @ STL   SO
  ```

  Derived from `data.games[]` in `team_schedule_stl.json`, filtered to `gameType == 2` (regular season) and `gameState == "OFF"` (completed), classified REG/OT/SO via `gameOutcome.lastPeriodType`. Task 1 should hardcode this list directly (e.g. as a module-level constant) rather than re-deriving it from the schedule endpoint at runtime — the schedule fetch would add an extra API dependency for no benefit at this fixed-list stage.

- **Phase 5 timing:** Deferred. Stop after the Phase 4/MVP checkpoint; do not start Phase 5 until there's a concrete analysis use case pulling on `mart_nhl__player_on_ice_impact` / `mart_nhl__team_shot_quality`, mirroring the still-unstarted shift-charts work (issue #5).

## Open Questions

- **Full-season backfill and incremental loading** are explicitly out of scope for this plan (matches the spec's own acknowledgment that this is a large lift). Should be scoped as a separate follow-up plan once the MVP marts are validated.
