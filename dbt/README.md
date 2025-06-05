# nhl-data dbt project

dbt project for sourcing and transforming NHL data

## Setup and Prerequisites

Local development

- using `uv` for Python package management.

Connecting to data

To have dbt access S3, and optionally Motherduck, copy the `.env` file as follows:

```bash
cp .env.example .env
```

And fill out the values in the newly created `.env` file

Then run dbt with `uv` as shown below

Note, the `--env-file` flag tells uv to load environment variables from the specified `.env` file (alternatively, set the environment variable: UV_ENV_FILE)

```bash
# Read values from .env into environment variables (referenced with env_var in dbt project)
export $(grep -v '^#' .env | xargs)

# Do dbt stuff (replace everything after "dbt" with whatever you need)
uv run dbt debug --target dev

# And just for reference, you can avoid having to use the "export" step above if you pass in the --env-file parameter to uv run like this:
uv run --env-file .env dbt debug --target dev
```

