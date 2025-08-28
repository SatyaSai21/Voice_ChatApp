import boto3
import os
from urllib.parse import quote


from botocore.exceptions import NoCredentialsError

AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET = os.getenv("AWS_BUCKET_NAME")

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

def upload_file_to_s3(file_bytes, key, content_type="application/octet-stream"):
    """
    Uploads file to S3 with public access and returns permanent public URL.
    """
    try:
        s3_client.put_object(
            Bucket=AWS_BUCKET,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
            ACL="public-read"  
        )
        # Permanent public URL
        url = f"https://{AWS_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{quote(key)}"
        return url
    except NoCredentialsError:
        raise Exception("AWS credentials not found")

def generate_presigned_url(key, expires=3600):
    """
    Generate a temporary presigned URL for secure file download.
    """
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": AWS_BUCKET, "Key": key},
        ExpiresIn=expires,
    )
