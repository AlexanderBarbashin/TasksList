import logging

import boto3
from os import environ
from botocore.exceptions import ClientError


def update_main_page(s3_client):
    bucket = environ['S3_BUCKET_NAME']
    try:
        response = s3_client.upload_file('web/index.html', bucket, 'index.html',
                                         ExtraArgs={'ContentType': 'text/html'})
    except ClientError as e:
        logging.error(e)
        return False
    return True


if __name__ == "__main__":
    region = environ['AWS_REGION']
    client = boto3.client('s3', region)
    update_main_page(client)
