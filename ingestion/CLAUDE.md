# CLAUDE.md — ingestion/

## Commands

### Setup (from repo root)
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

### Lint/format (from ingestion/)
```bash
uv run ruff check .     # Lint
uv run ruff format .    # Format
```
`src/nhl_proj_lineup/` is excluded (orphaned/WIP, not in the packaged wheel).
