import boto3
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
load_dotenv()

from config import Config

session = boto3.session.Session()
s3 = session.client(
    "s3",
    endpoint_url=Config.S3_ENDPOINT,
    aws_access_key_id=Config.S3_ACCESS_KEY,
    aws_secret_access_key=Config.S3_SECRET_KEY
)

def upload_file_to_s3(local_path: str, s3_key: str) -> str:
    bucket = Config.S3_BUCKET
    s3.upload_file(local_path, bucket, s3_key)
    return f"{Config.S3_ENDPOINT}/{bucket}/{s3_key}"

def delete_file_from_s3(file_url: str):
    bucket = Config.S3_BUCKET
    key = "/".join(urlparse(file_url).path.lstrip("/").split("/")[1:])
    try:
        s3.delete_object(Bucket=bucket, Key=key)
    except Exception as e:
        print("Error deleting S3 object:", e)
