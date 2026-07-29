# NHL Data Project

A data engineering project for NHL hockey data analysis.

## Architecture

```text
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

![dbt DAG](./docs/dbt_dag.png)

## Project Structure

- `ingestion/`: Data ingestion from NHL API and MoneyPuck
  - `src/`: Source packages (nhl_api, moneypuck, utility)
  - `scripts/`: Entry point scripts
- `dbt/`: dbt project for data transformation
- `data/`: Local data storage (git-ignored)

## Getting Started

1. Clone the repository
1. Set up Python environment (with uv):
    ```bash
    uv venv
    uv sync
    ```
1. Set up environment variables:
   1. Create .env file 
    ```bash
    cp .env.example .env
    ```
    1. Edit .env with your configuration
1. Run the data acquisition scripts:
    ```bash
    uv run python ingestion/scripts/nhl_api/get_nhl_api_data.py
    uv run python ingestion/scripts/get_moneypuck_data.py
    uv run python ingestion/scripts/write_moneypuck_to_s3.py
    ```
    The NHL play-by-play pipeline scripts (`get_nhl_play_by_play.py`, `get_nhl_boxscores.py`,
    `write_nhl_api_to_s3.py`) must be run with cwd = `ingestion/scripts/` — see `ingestion/CLAUDE.md`.
1. Run dbt models:
    ```bash
    deactivate
    cd $(git rev-parse --show-toplevel)/dbt
    uv venv && uv sync
    uv run --env-file .env dbt deps
    uv run --env-file .env dbt build
    ```

## Data Sources

### NHL API: Official NHL statistics API

### MoneyPuck.com: Advanced hockey statistics

### Entity coverage

Key:
- ✅: Data source has it & it's modeled in dbt
- 🚧: Data source has it & dbt modeling is incomplete
- ❌: Data source doesn't have this entity

| Entity | MoneyPuck | NHL API | Notes |
|---|---|---|---|
| Season | ✅ | ✅ | MoneyPuck has season-level summary data for teams, goalies, lines, and skaters |
| Game | ✅ | ✅ | |
| Line | ✅ | ❌ | |
| Player | ✅ | ✅ | NHL API: player info, game logs, stats leaders |
| Play | ❌ | ✅ | `nhl_api.resources.games.get_play_by_play`; modeled through `int_nhl__events_enriched` / `fct_nhl__player_game_events` |
| Shot | ✅ | ✅ | MoneyPuck: season/game shot data. NHL API: derived from play-by-play via `int_nhl__shot_events` / `fct_nhl__shot_attempts` |
| Team | ✅ | ✅ | |

For active/planned work, see [`tasks/`](tasks/) — this table only reflects what's already built.

## License

MIT
