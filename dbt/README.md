# nhl-data dbt project

dbt project for sourcing and transforming NHL data

## Setup and Prerequisites

Local development

- using `uv` for Python package management.

Connecting to data

The `dev` target writes to a local DuckDB file. The `prod` target connects to MotherDuck. Both read source data from S3.

1. Copy the example env file and fill in your credentials:

```bash
cp .env.example .env
```

You need `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` for both targets. `MOTHERDUCK_TOKEN` is only needed for the `prod` target (get it from your MotherDuck account settings).

1. Run dbt with environment variables loaded:

```bash
# Option A: export from .env first
export $(grep -v '^#' .env | xargs)
uv run dbt debug --target dev

# Option B: use uv's --env-file flag (no export needed)
uv run --env-file .env dbt debug --target dev
```
