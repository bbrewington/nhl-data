# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NHL hockey data engineering pipeline with two main layers:
1. **Python data acquisition** (`python/`) - fetches data from NHL API and MoneyPuck.com, stages locally, uploads to S3 as Parquet
2. **dbt transformations** (`dbt/`) - transforms S3-hosted Parquet data using dbt-duckdb with MotherDuck for analytics

These are **separate Python environments** managed with `uv`, each with their own `pyproject.toml` and virtual environment.

## Commands

### Python environment (from repo root)
```bash
cd python && uv venv && uv sync       # Setup
uv run python scripts/get_nhl_api_data.py
uv run python scripts/get_moneypuck_data.py
uv run python scripts/write_moneypuck_to_s3.py
```

### Tests (from python/)
```bash
pytest                        # All tests
pytest -m unit                # Unit tests only
pytest -m integration         # Integration tests only
pytest -m "not slow"          # Skip slow tests
pytest --snapshot-update      # Update test snapshots
```

### dbt environment (from dbt/)
```bash
cd dbt && uv venv && uv sync          # Setup (separate venv from python/)
cp profiles.yml.example profiles.yml  # Configure connection (dev=local DuckDB, prod=MotherDuck)
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
  python/src/          ← Python acquisition (requests + backoff, BeautifulSoup)
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

## Dual directory note

`get_data/` contains an older/alternative structure with READMEs documenting NHL API endpoints and MoneyPuck data. The active code lives in `python/src/`.
