# NHL Data Project

A data engineering project for NHL hockey data analysis.

## Project Structure

- `python/`: Python code for data acquisition and processing
  - `nhl_data/`: Main package
  - `scripts/`: Entry point scripts
  - `tests/`: Unit and integration tests
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
    uv run python python/scripts/get_nhl_api_data.py
    uv run python python/scripts/get_moneypuck_data.py
    ```
1. Run dbt models:
    ```bash
    deactivate
    cd $(git rev-parse --show-toplevel)/dbt
    uv venv
    uv run dbt deps
    uv run dbt build
    ```

## Data Sources

### NHL API: Official NHL statistics API

### MoneyPuck.com: Advanced hockey statistics

## License

MIT


## Test Notes

### Running Tests
#### Basic test run
```bash
pytest
```
Run with coverage
```bash
bashpytest --cov=nhl_api --cov-report=html
```

Run specific test categories

Unit tests only
```bash
pytest -m unit
```

Integration tests only
```bash
pytest -m integration
```

Skip slow tests
```bash
pytest -m "not slow"
```

Update snapshots
```bash
pytest --snapshot-update
```

Update specific test snapshots
```bash
pytest test_integration.py::TestNHLClientIntegration::test_get_team_stats_season_snapshot --snapshot-update
```
