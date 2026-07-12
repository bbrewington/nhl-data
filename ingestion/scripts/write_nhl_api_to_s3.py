from pathlib import Path
from dotenv import load_dotenv
from utility.aws import run_s3_upload_fileext

load_dotenv()
DATA_DIR = Path("../data/nhl_api")

# nhl_api layout is 4 levels deep (nhl_api/{dataset}/game_id={id}/{file}.parquet),
# vs. moneypuck's 3 (moneypuck/{dataset}/{file}.parquet) - keep all 4 in the S3 key.
run_s3_upload_fileext(data_dir=DATA_DIR, file_ext="parquet", num_key_parts=4)
