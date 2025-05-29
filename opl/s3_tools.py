import logging
import boto3
import botocore.client
from typing import List, Dict, Union


def connect(s3_conf: Dict) -> boto3.resource:
    """
    Connect to s3
    Args:
        s3_conf: all aws access credentials like access_key, secret_key, region, etc.
    Returns:
        s3 connection object
    """
    logging.debug("Going to connect")
    s3_resource = boto3.resource(
        "s3",
        aws_access_key_id=s3_conf["aws_access_key_id"],
        aws_secret_access_key=s3_conf["aws_secret_access_key"],
        region_name=s3_conf["aws_region"],
        config=botocore.config.Config(signature_version="s3v4"),
    )
    logging.debug("Connected")
    return s3_resource


def upload_file(s3_resource, local_name, bucket, remote_name):
    logging.debug(f"Going to upload {local_name}")
    s3_bucket = s3_resource.Bucket(name=bucket)
    s3_object = s3_bucket.Object(key=remote_name)
    s3_object.upload_file(
        Filename=local_name, ExtraArgs={"ServerSideEncryption": "AES256"}
    )
    size = s3_object.content_length
    logging.info(f"Uploaded {size}B of {local_name} as {remote_name}")
    return size


def get_presigned_url(s3_resource, bucket, remote_name):
    logging.debug(f"Going to generate signed URL for {remote_name}")
    download_url = s3_resource.meta.client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": bucket,
            "Key": remote_name,
        },
        ExpiresIn=3600 * 3,
    )
    logging.info(f"For {remote_name} obtained signed url {download_url}")
    return download_url


def delete_files(
    s3_resource: boto3.resource, bucket_name: str, file_paths: Union[str, List[str]]
) -> Union[Dict, bool]:
    """
    Delete s3-objets from s3 bucket
    Args:
        s3_resource: create s3 resource object from using connect() and pass
        bucket_name: s3 bucket name
        file_paths: filename or list of file names you want to delete
    Returns:
        Delete response or False
    """
    # Create a list of objects to delete
    if isinstance(file_paths, list):
        objects_to_delete = [{"Key": path} for path in file_paths]
    elif isinstance(file_paths, str):
        objects_to_delete = [{"Key": file_paths}]
    else:
        print(f"file_paths attribute must be string or list not {type(file_paths)}")
        return False
    logging.debug("Going to delete")
    if objects_to_delete:
        response = s3_resource.meta.client.delete_objects(
            Bucket=bucket_name, Delete={"Objects": objects_to_delete}
        )
        logging.debug("object/objects deleted")
        return response
