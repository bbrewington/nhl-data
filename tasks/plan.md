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
- **New `stg_nhl_api__games` staging model, added when starting Phase 3.** `int_nhl__events_enriched` needs `is_home_team_event`, but no staged table records which numeric NHL API `team_id` is home vs. away, and there's no crosswalk from that numeric id to `team_abbr` (`stg__team_abbrs`/`int__players` are keyed off MoneyPuck's `team_abbr_raw` instead). Checked against the real captured API response, the play-by-play payload's top-level `homeTeam`/`awayTeam` objects carry both `id` and `abbrev` directly — `get_nhl_play_by_play.py` just wasn't capturing them. New Task 8 extends that script, re-runs ingestion/upload for the existing 21-game list, and adds a small staging model; this also means `int_nhl__events_enriched` doesn't need a `stg__team_abbrs` crosswalk at all. All task numbers from Phase 3 onward shifted by +1 to make room (old Task 8 → 9, ... old Task 15 → 16).

## Task List

Per-task/per-checkpoint detail (description, acceptance criteria, verification, evidence) lives in
[tasks/todo.md](todo.md) — this section is just a phase-level status index.

### Phase 1: Ingestion
✅ Complete — Tasks 1-3 + checkpoint, see [tasks/todo.md](todo.md)

### Phase 2: dbt Staging
✅ Complete — Tasks 4-7 + checkpoint, see [tasks/todo.md](todo.md)

### Phase 3: dbt Intermediate
✅ Complete — Tasks 8-11 + checkpoint, see [tasks/todo.md](todo.md)

### Phase 4: dbt Marts (MVP)
✅ Complete — Tasks 12-14 + checkpoint, see [tasks/todo.md](todo.md)
- [ ] Ready for human review before starting Phase 5

### Phase 5: dbt Marts (Stretch — separate review checkpoint)
☐ Not started — Tasks 15-16, see [tasks/todo.md](todo.md). Deferred per Resolved Decisions below.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec assumes dlt/Pydantic ingestion; adapting to plain-script pattern means losing schema validation on ingest | Med | Rely on dbt schema tests (accepted_values, not_null, bounds checks) as the validation layer instead — same approach already used for MoneyPuck data |
| `game_id=*` Hive-partitioned glob may not work cleanly in dbt-duckdb (unconfirmed — same open risk flagged in the shift-charts doc) | Med | Task 4 validates this first, before staging models are built on top; fallback is a flat `shift_charts/*` style glob |
| Coordinate normalization (which end each team shoots at, per period) is empirically determined, not documented by the API | High | Task 9 validates against known shot-on-goal patterns before downstream models depend on it; get this right early since everything in Phase 3+ depends on it |
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
