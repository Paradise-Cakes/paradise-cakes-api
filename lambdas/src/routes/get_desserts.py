import boto3
import os
from fastapi import APIRouter
from aws_lambda_powertools import Logger
from fastapi.exceptions import HTTPException
from src.models import Dessert
from src.lib.dynamodb import DynamoConnection
from src.lib.response import fastapi_gateway_response


logger = Logger()
router = APIRouter()

desserts_table = DynamoConnection(
    os.environ.get("DYNAMODB_REGION", "us-east-1"),
    os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    os.environ.get("DYNAMODB_DESSERTS_TABLE_NAME", "desserts"),
).table


@logger.inject_lambda_context(log_event=True)
@router.get(
    "/desserts",
    status_code=200,
)
def get_desserts(dessert_type: str):
    logger.info(f"Getting desserts")

    dynamo_response = desserts_table.query(
        IndexName="dessert-type-index",
        KeyConditionExpression="dessert_type = :dessert_type",
        ExpressionAttributeValues={":dessert_type": dessert_type},
    )

    if "Items" not in dynamo_response:
        raise HTTPException(status_code=404, detail="No desserts found")

    desserts = [Dessert(**d).clean() for d in dynamo_response.get("Items")]

    logger.info(f"Returning {len(desserts)} desserts")
    return fastapi_gateway_response(200, {}, desserts)
