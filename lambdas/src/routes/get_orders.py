import os

import boto3
from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Key
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from src.lib.dynamodb import DynamoConnection
from src.lib.response import fastapi_gateway_response
from src.models import Order

logger = Logger()
router = APIRouter()

orders_table = DynamoConnection(
    os.environ.get("DYNAMODB_REGION", "us-east-1"),
    os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    os.environ.get("DYNAMODB_ORDERS_TABLE_NAME", "orders"),
).table


@logger.inject_lambda_context(log_event=True)
@router.get(
    "/orders",
    status_code=200,
    tags=["Orders"],
)
def get_orders(
    order_date: str = None, customer_full_name: str = None, delivery_date: str = None
):
    if delivery_date:
        logger.info(f"Getting orders for delivery date {delivery_date}")
        dynamo_response = orders_table.query(
            IndexName="delivery_date_index",
            KeyConditionExpression=Key("delivery_date").eq(delivery_date),
        )
    elif customer_full_name:
        logger.info(f"Getting orders for customer {customer_full_name}")
        dynamo_response = orders_table.query(
            IndexName="customer_full_name_index",
            KeyConditionExpression=Key("customer_full_name").eq(customer_full_name),
        )
    elif order_date:
        logger.info(f"Getting orders for order date {order_date}")
        dynamo_response = orders_table.query(
            IndexName="order_date_index",
            KeyConditionExpression=Key("order_date").eq(order_date),
        )
    else:
        raise HTTPException(status_code=400, detail="Missing query parameter")

    if "Items" not in dynamo_response:
        raise HTTPException(status_code=404, detail="No orders found")

    logger.info(f"Found {len(dynamo_response.get('Items'))} orders")
    logger.info(dynamo_response.get("Items"))

    orders = [Order(**o).clean() for o in dynamo_response.get("Items")]

    logger.info(f"Returning {len(orders)} orders")
    return fastapi_gateway_response(200, {}, orders)
