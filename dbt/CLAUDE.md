# CLAUDE.md — dbt/

## Commands

### Setup (from dbt/)
```bash
cd dbt && uv venv && uv sync          # Setup (separate venv from ingestion/)
# profiles.yml already exists (gitignored) — dev=local DuckDB, prod=MotherDuck
cp .env.example .env                  # Set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, MOTHERDUCK_TOKEN
uv run --env-file .env dbt deps       # Install dbt packages
uv run --env-file .env dbt build      # Build all models + run tests
uv run --env-file .env dbt run --select stg_moneypuck__players  # Run single model
uv run --env-file .env dbt test       # Run dbt tests only
```
