"""Configuration settings for the NHL data project."""

import os
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parents[3]  # nhl-data/
DATA_DIR = PROJECT_ROOT / "data"

# Raw data paths
RAW_DATA_DIR = DATA_DIR / "raw"
NHL_RAW_DIR = RAW_DATA_DIR / "nhl"
MONEYPUCK_RAW_DIR = RAW_DATA_DIR / "moneypuck"

# Processed data
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# S3 configuration
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_PREFIX = os.environ.get("S3_PREFIX", "nhl-data/")

# NHL API configuration
NHL_API_BASE_URL = "https://statsapi.web.nhl.com/api/v1"

# Ensure directories exist
for dir_path in [NHL_RAW_DIR, MONEYPUCK_RAW_DIR, PROCESSED_DATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
