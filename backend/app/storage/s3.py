import boto3
from botocore.client import Config

from app.core.config import Settings
from app.storage.base import StorageService


class S3StorageService(StorageService):
    provider_name = "s3"

    def __init__(self, settings: Settings) -> None:
        required = {
            "S3_ENDPOINT_URL": settings.s3_endpoint_url,
            "S3_ACCESS_KEY_ID": settings.s3_access_key_id,
            "S3_SECRET_ACCESS_KEY": settings.s3_secret_access_key,
            "S3_BUCKET_NAME": settings.s3_bucket_name,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(f"Missing S3 configuration: {', '.join(missing)}")

        self.bucket_name = settings.s3_bucket_name or ""
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            region_name=settings.s3_region,
            config=Config(signature_version="s3v4"),
        )

    async def save(self, object_key: str, content: bytes, content_type: str) -> str:
        self.client.put_object(
            Bucket=self.bucket_name,
            Key=object_key,
            Body=content,
            ContentType=content_type,
        )
        return object_key

    async def read(self, object_key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket_name, Key=object_key)
        return response["Body"].read()

    async def delete(self, object_key: str) -> None:
        self.client.delete_object(Bucket=self.bucket_name, Key=object_key)
