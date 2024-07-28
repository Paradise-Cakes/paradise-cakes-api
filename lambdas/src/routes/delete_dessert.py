import os
import boto3
from fastapi import APIRouter, Request
from aws_lambda_powertools import Logger
from fastapi.exceptions import HTTPException
from src.lib.response import fastapi_gateway_response
from src.models import (
    Dessert,
)
from src.lib.dynamodb import DynamoConnection

logger = Logger()
router = APIRouter()

desserts_table = DynamoConnection(
    os.environ.get("DYNAMODB_REGION", "us-east-1"),
    os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    os.environ.get("DYNAMODB_DESSERTS_TABLE_NAME", "desserts"),
).table


s3_client = boto3.client("s3")


class DeleteDessertResponse(Dessert):
    pass


@logger.inject_lambda_context(log_event=True)
@router.delete(
    "/desserts/{dessert_id}",
    status_code=200,
    response_model=DeleteDessertResponse,
)
def delete_dessert(request: Request, dessert_id: str):
    logger.info(f"Deleting dessert with ID: {dessert_id}")

    get_dessert_response = desserts_table.get_item(Key={"dessert_id": dessert_id})
    if "Item" not in get_dessert_response:
        raise HTTPException(status_code=404, detail="Dessert not found")

    # check if the dessert has any images and delete them
    if "images" in get_dessert_response["Item"]:
        for image in get_dessert_response["Item"]["images"]:
            bucket_name = os.environ.get("DESSERT_IMAGES_BUCKET_NAME")
            s3_client.delete_object(
                Bucket=bucket_name, Key=f"{dessert_id}/{image['image_id']}"
            )

    desserts_table.delete_item(Key={"dessert_id": dessert_id})
    response = DeleteDessertResponse(**get_dessert_response["Item"])
    logger.info(f"Deleted dessert: {response}") 
    return fastapi_gateway_response(200, {}, response.clean())
