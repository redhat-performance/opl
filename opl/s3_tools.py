import logging

import boto3

import botocore.client


def connect(s3_conf):
    logging.debug(f"Going to connect")
    s3_resource = boto3.resource(
        's3',
        aws_access_key_id=s3_conf['aws_access_key_id'],
        aws_secret_access_key=s3_conf['aws_secret_access_key'],
        region_name=s3_conf['aws_region'],
        config=botocore.config.Config(signature_version='s3v4'),
    )
    logging.debug(f"Connected")
    return s3_resource


def upload_file(s3_resource, local_name, bucket, remote_name):
    logging.debug(f"Going to upload {local_name}")
    s3_bucket = s3_resource.Bucket(name=bucket)
    s3_object = s3_bucket.Object(key=remote_name)
    s3_object.upload_file(Filename=local_name, ExtraArgs={'ServerSideEncryption': 'AES256'})
    size = s3_object.content_length
    logging.info(f"Uploaded {size}B of {local_name} as {remote_name}")
    return size


def get_presigned_url(s3_resource, bucket, remote_name):
    logging.debug(f"Going to generate signed URL for {remote_name}")
    download_url = s3_resource.meta.client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket,
            'Key': remote_name,
        },
        ExpiresIn=3600 * 3,
    )
    logging.info(f"For {remote_name} obtained signed url {download_url}")
    return download_url
