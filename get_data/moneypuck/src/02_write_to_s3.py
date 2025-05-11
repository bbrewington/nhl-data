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

def upload_file(file_path: Path, bucket_name, dest_object_name, verbose=False):
    if verbose:
        print(f"Writing {file_path} to s3://{bucket_name}/{dest_object_name}")
    
    with file_path.open("rb") as f:
        s3.upload_fileobj(f, bucket_name, dest_object_name)

if __name__ == "__main__":
    csv_files = DATA_DIR.glob("**/*.csv")
    assert len(csv_files) > 0, "No CSV files found"
    for csv_file in csv_files:
        dest_object_name = "/".join(csv_file.parts[-3:])
        upload_file(file_path=csv_file, bucket_name=S3_BUCKET, dest_object_name=dest_object_name, verbose=True)
