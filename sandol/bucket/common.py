import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

BUCKET_NAME = "sandol-bucket"
FILE_KEY = "test.json"


def get_s3_client():
    return boto3.client('s3')


def download_file_from_s3(bucket_name, file_key, download_path):
    s3 = get_s3_client()
    try:
        s3.download_file(bucket_name, file_key, download_path)
    except (NoCredentialsError, PartialCredentialsError):
        logger.error("AWS 자격 증명이 필요합니다.")
        raise
    except s3.exceptions.NoSuchKey as exeception:
        logger.error(f"{file_key} 파일을 찾을 수 없습니다.")
        raise FileNotFoundError(f"{file_key} 파일을 찾을 수 없습니다.") from exeception


def upload_file_to_s3(file_path, bucket_name, file_key):
    s3 = get_s3_client()
    try:
        s3.upload_file(file_path, bucket_name, file_key)
    except (NoCredentialsError, PartialCredentialsError):
        logger.error("AWS 자격 증명이 필요합니다.")
        raise
