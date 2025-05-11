# moneypuck/

The 'moneypuck/' folder contains a project that downloads and processes NHL data from various sources. This data is then loaded into an S3 bucket and queried using dbt-duckdb and Motherduck.

## Prerequisites

- Python 3.12 (managed using uv for environment management)
- The following Python dependencies:
  - beautifulsoup4
  - dbt-duckdb
  - duckdb
  - pandas
  - requests

## Data

The data loaded into this project comes from the URLs specified in the `hockey_stats_links.csv` file. This includes CSV files containing information about:

- Skaters
- Goalies
- Line combinations
- Team details

The downloaded data is stored in the `data/` subfolder (which is meant to be local staging, and is included in .gitignore)

## Quickstart

1. Set up the Python environment using uv:
    ```
    cd $(git rev-parse --show-toplevel)/get_data/moneypuck
    uv sync
    ```

2. Run the data download and load scripts:
    ```
    uv run python src/get_data.py
    ```

3. Query the data using dbt-duckdb and Motherduck:
   ```
   dbt run --models stg__test_table
   ```

   This will load the data into an S3 bucket and allow you to run SQL queries against it.

## Tech Debt to Fix

- TODO: Templatize the URL's in [config/dir_file_url_config.json](config/dir_file_url_config.json) so it's not hard-coded to a particular year
