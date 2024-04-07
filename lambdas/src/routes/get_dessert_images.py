import os 
import boto3
from fastapi import APIRouter, Request
from aws_lambda_powertools import Logger
from src.lib.response import fastapi_gateway_response
from src.models import DessertImage
from src.lib.dynamodb import DynamoConnection

logger = Logger()
router = APIRouter()

dessert_images_table = DynamoConnection(
    os.environ.get("DYNAMODB_REGION", "us-east-1"),
    os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    os.environ.get("DYNAMODB_DESSERT_IMAGES_TABLE_NAME", "dessert_images"),
).table


@logger.inject_lambda_context(log_event=True)
@router.get(
    "/desserts/{dessert_id}/images",
    status_code=200,
    response_model=list[DessertImage],
)
def get_dessert_images(dessert_id: str):
    logger.info(f"Getting images for dessert: {dessert_id}")

    response = dessert_images_table.query(
        KeyConditionExpression="dessert_id = :dessert_id",
        ExpressionAttributeValues={":dessert_id": dessert_id},
    )

    if "Items" not in response:
        return fastapi_gateway_response(200, {}, [])

    images = [DessertImage(**i).clean() for i in response.get("Items")]
    images.sort(key=lambda x: x["position"])

    logger.info(images)

    logger.info(f"Returning {len(images)} images")
    return fastapi_gateway_response(200, {}, images)