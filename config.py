import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///documents.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    S3_BUCKET = os.getenv("S3_BUCKET", "local-bucket")
    S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")  # MinIO
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "your-google-api-key")
