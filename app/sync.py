import boto3


def test_connection(config: dict):
    s3 = boto3.client(
        "s3",
        endpoint_url=config["endpoint"],
        aws_access_key_id=config["access_key"],
        aws_secret_access_key=config["secret_key"],
    )

    s3.list_objects_v2(Bucket=config["bucket"], MaxKeys=1)
