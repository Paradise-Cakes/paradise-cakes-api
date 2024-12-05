import os

import boto3
from aws_lambda_powertools import Logger
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from src.lib.response import fastapi_gateway_response

logger = Logger()
router = APIRouter()
s3_client = boto3.client("s3")


@logger.inject_lambda_context(log_event=True)
@router.get(
    "/display-images",
    status_code=200,
)
def get_display_images():
    logger.info(f"Getting display images")

    bucket_name = os.environ.get("DESSERT_IMAGES_BUCKET_NAME")
    prefix = "homepage-display/"
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    if "Contents" not in response:
        raise HTTPException(status_code=404, detail="No display images found")

    urls = []
    for obj in response["Contents"]:
        # Construct the public URL for each object
        url = f"https://{bucket_name}.s3.amazonaws.com/{obj['Key']}"
        urls.append(url)

    urls.pop(0)
    return fastapi_gateway_response(200, {}, urls)
