import boto3
from pathlib import Path
from dotenv import load_dotenv
import os

# Note, when you see "../" in this file, it is relative to working dir
# where the script is run (not necessarily this .py file)
# HACK: There's probably a more elegant way to do this

load_dotenv("../.env")

DATA_DIR = Path("../data/moneypuck")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")

s3 = boto3.client('s3')

def upload_file_to_s3(file_path: Path, bucket_name, dest_object_name, verbose=False):
    if verbose:
        print(f"Writing {file_path} to s3://{bucket_name}/{dest_object_name}")
    
    with file_path.open("rb") as f:
        s3.upload_fileobj(f, bucket_name, dest_object_name)

def run_s3_upload_fileext(data_dir, file_ext):
    files = [x for x in data_dir.glob(f"**/*.{file_ext}")]
    assert len(files) > 0, f"No files of type {file_ext} found in {data_dir}"
    for file in files:
        dest_object_name = "/".join(file.parts[-3:])
        upload_file_to_s3(file_path=file, bucket_name=S3_BUCKET, dest_object_name=dest_object_name, verbose=True)

if __name__ == "__main__":
    run_s3_upload_fileext(data_dir=DATA_DIR, file_ext="parquet")
