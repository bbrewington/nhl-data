# nhl-data dbt project

Note, this repo is using `uv` for Python package management.

To have dbt access S3, and optionally Motherduck, copy the `.env` file as follows:

```bash
cp .env.example .env
```

And fill out the values in the newly created `.env` file

Then run dbt with `uv` as shown below

Note, the `--env-file` flag tells uv to load environment variables from the specified `.env` file (alternatively, set the environment variable: UV_ENV_FILE)

```bash
uv run --env-file .env dbt debug --target dev
```

