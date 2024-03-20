import boto3
import os
from fastapi import APIRouter
from aws_lambda_powertools import Logger
from fastapi.exceptions import HTTPException
from src.models import Order
from src.lib.dynamodb import DynamoConnection

logger = Logger()
router = APIRouter()


dynamodb_table = DynamoConnection(
    os.environ.get("DYNAMODB_REGION", "us-east-1"),
    os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    os.environ.get("DYNAMODB_ORDERS_TABLE_NAME", "orders"),
).table


@logger.inject_lambda_context
@router.get(
    "/orders",
    status_code=200,
)
def get_orders():
    logger.info(f"Getting orders")

    dynamo_response = dynamodb_table.scan()

    if "Items" not in dynamo_response:
        raise HTTPException(status_code=404, detail="No orders found")

    orders = [Order(**o).clean() for o in dynamo_response.get("Items")]

    logger.info(f"Returning {len(orders)} desserts")
    return {"orders": orders}
