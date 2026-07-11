# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NHL hockey data engineering pipeline with two main layers:
1. **Data ingestion** (`ingestion/`) - fetches data from NHL API and MoneyPuck.com, stages locally, uploads to S3 as Parquet
2. **dbt transformations** (`dbt/`) - transforms S3-hosted Parquet data using dbt-duckdb with MotherDuck for analytics

These are **separate Python environments** managed with `uv`, each with their own `pyproject.toml` and virtual environment.

## Commands

### Ingestion environment (from repo root)
```bash
cd ingestion && uv venv && uv sync    # Setup
uv run python scripts/nhl_api/get_nhl_api_data.py
uv run python scripts/get_moneypuck_data.py
uv run python scripts/write_moneypuck_to_s3.py
```

### Tests (from ingestion/)
```bash
uv run pytest                 # All tests — no network/AWS access required
uv run pytest -m "not slow"   # Skip slow tests (no tests marked slow yet)
uv run pytest tests/nhl_api/test_teams.py -v   # Single file
```
Tests mock at the `NHLSession.get_url` / `requests` / `boto3` boundary; `nhl_api` resource tests reuse the captured fixtures in `src/nhl_api/example_responses/*.json` via the `example_response` fixture in `tests/conftest.py`. `tests/` mirrors `src/` 1:1.

### dbt environment (from dbt/)
```bash
cd dbt && uv venv && uv sync          # Setup (separate venv from ingestion/)
# profiles.yml already exists (gitignored) — dev=local DuckDB, prod=MotherDuck
cp .env.example .env                  # Set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, MOTHERDUCK_TOKEN
uv run --env-file .env dbt deps       # Install dbt packages
uv run --env-file .env dbt build      # Build all models + run tests
uv run --env-file .env dbt run --select stg_moneypuck__players  # Run single model
uv run --env-file .env dbt test       # Run dbt tests only
```

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
  S3 (Parquet)         ← s3://bbrewington-nhl-data/moneypuck/
        │
        ▼
  dbt/ (dbt-duckdb)    ← SQL transformations against S3 sources
  staging/             ← stg_* models (materialized: table)
  intermediate/        ← int_* models (materialized: view)
  snapshots/           ← SCD Type 2 player tracking
        │
        ▼
  DuckDB / MotherDuck  ← Analytics queries
```

### Data sources defined in `dbt/models/staging/_sources.yml`
- S3 external source `s3__bbrewington_nhl_data__moneypuck` with glob patterns for season-level, game-level, and shots data

### Key dbt macro
- `game_id_attrs(game_id_colname)` in `dbt/macros/game_id_attrs.sql` - parses NHL 10-digit game IDs into game_type, game_number, and playoff metadata

### SCD snapshot pattern
- `dbt/snapshots/*.yml` (YAML-only dbt snapshots, e.g. `snapshot__all_players_lookup`) track SCD Type 2 history directly off S3 sources
- `staging/**/base/` models (e.g. `stg_moneypuck__players_hist.sql`) select from a snapshot and do the real column parsing/renaming
- The non-`base` staging model of the same name (e.g. `stg_moneypuck__players.sql`) just filters the `base` model to current rows (`dbt_valid_to is null and dbt_is_deleted = FALSE`) — edit the `base` model, not the wrapper, when changing transformation logic

### Entity model
See `docs/erd.md` for the Mermaid ERD covering Season, Game, Team, Player, Play, Shot, Goal, Penalty relationships.

## Conventions

- **Python:** requires >= 3.13, uses `uv` for package management, `hatchling` build backend
- **dbt project name:** `nhl_dbt`, profile: `nhl_dbt`
- **dbt model naming:** `stg_<source>__<entity>` for staging, `int__<entity>` for intermediate, `seed__<entity>` for seeds
- **NHLClient** supports context manager: `with NHLClient() as client:`
- **HTTP retry:** NHLSession uses `backoff.on_exception` with exponential backoff on timeouts/connection errors
- **Data formats:** Parquet for storage, CSV seeds for reference data
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
