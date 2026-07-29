# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NHL hockey data engineering pipeline with two main layers:
1. **Data ingestion** (`ingestion/`) - fetches data from NHL API and MoneyPuck.com, stages locally, uploads to S3 as Parquet
2. **dbt transformations** (`dbt/`) - transforms S3-hosted Parquet data using dbt-duckdb with MotherDuck for analytics

These are **separate Python environments** managed with `uv`, each with their own `pyproject.toml` and virtual environment.

## Commands

See `ingestion/CLAUDE.md` for ingestion setup/test/lint commands and `dbt/CLAUDE.md` for dbt setup/build commands.

## Architecture

```
NHL API / MoneyPuck.com
        │
        ▼
  ingestion/src/       ← Data ingestion (requests + backoff, BeautifulSoup)
  nhl_api/client.py    ← NHLClient with resource pattern (.league, .teams, .players, .games)
  moneypuck/           ← CSV scraper, converts to Parquet
        │
        ▼
  S3 (Parquet)         ← s3://bbrewington-nhl-data/{moneypuck,nhl_api}/
        │
        ▼
  dbt/ (dbt-duckdb)    ← SQL transformations against S3 sources
  staging/             ← stg_* models (materialized: table)
  intermediate/        ← int_* models (materialized: view)
  marts/               ← fct_*/mart_* models (materialized: table)
  snapshots/           ← SCD Type 2 player tracking
        │
        ▼
  DuckDB / MotherDuck  ← Analytics queries
```

### Data sources defined in `dbt/models/staging/_sources.yml`
- S3 external source `s3__bbrewington_nhl_data__moneypuck` with glob patterns for season-level, game-level, and shots data
- S3 external source `s3__bbrewington_nhl_data__nhl_api` for play-by-play/boxscores/game_rosters/games, Hive-partitioned by `game_id=`. Uses `read_parquet(..., union_by_name=True)` as `external_location` since play-by-play event rows have type-specific `details_*` columns that vary file-to-file.

### Key dbt macro
- `game_id_attrs(game_id_colname)` in `dbt/macros/game_id_attrs.sql` - parses NHL 10-digit game IDs into game_type, game_number, and playoff metadata

### SCD snapshot pattern
- `dbt/snapshots/*.yml` (YAML-only dbt snapshots, e.g. `snapshot__all_players_lookup`) track SCD Type 2 history directly off S3 sources
- `staging/**/base/` models (e.g. `stg_moneypuck__players_hist.sql`) select from a snapshot and do the real column parsing/renaming
- The non-`base` staging model of the same name (e.g. `stg_moneypuck__players.sql`) just filters the `base` model to current rows (`dbt_valid_to is null and dbt_is_deleted = FALSE`) — edit the `base` model, not the wrapper, when changing transformation logic

### Entity model
See `docs/erd.md` for the Mermaid ERD covering Season, Game, Team, Player, Play, Shot, Goal, Penalty relationships.

## Conventions

- **dbt model naming:** `stg_<source>__<entity>` for staging, `int__<entity>` for intermediate, `seed__<entity>` for seeds. The NHL play-by-play pipeline (`docs/features/nhl_play_by_play.md`) instead namespaces intermediate/mart models by entity domain rather than source: `int_nhl__<entity>`, `fct_nhl__<entity>`, `mart_nhl__<entity>` (staging still follows the source-based `stg_nhl_api__<entity>` pattern)
- **NHLClient** supports context manager: `with NHLClient() as client:`
- **HTTP retry:** NHLSession uses `backoff.on_exception` with exponential backoff on timeouts/connection errors
- **Column naming:** snake_case (transformed from camelCase source data). MoneyPuck prefix conventions:
  - `x` prefix -> `exp_` (expected, e.g. `xGoals` -> `exp_goals`)
  - `I_F_` -> `ind_for_` (individual for)
  - `OnIce_F_` / `OnIce_A_` -> `on_ice_for_` / `on_ice_against_`
  - `OffIce_F_` / `OffIce_A_` -> `off_ice_for_` / `off_ice_against_`
  - `penality` (source typo) -> `penalty`
- **Team abbreviations:** normalized to 3-letter codes (handles variants like "S.J" -> "SJS") via `stg__team_abbrs`. Note: `stg__teams` has separate active/inactive era rows per `team_abbr` — use `select distinct team_abbr, team_name` when joining to avoid fan-out
- **DuckDB reserved words:** `freeze` must be quoted as `"freeze"` in SQL when used as a bare column name

## Directory structure note

`ingestion/` and `dbt/` are **separate Python environments** — each has its own `pyproject.toml`, `uv.lock`, and virtual environment.
