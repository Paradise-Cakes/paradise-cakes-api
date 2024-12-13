import os

from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Key
from fastapi import APIRouter
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


class GetOrderResponse(Order):
    pass


@logger.inject_lambda_context(log_event=True)
@router.get(
    "/orders/{order_id}",
    status_code=200,
    response_model=GetOrderResponse,
    tags=["Orders"],
)
def get_order(order_id: str):
    logger.info(f"Getting order with order_id {order_id}")

    orders_response = orders_table.get_item(
        TableName="orders", Key={"order_id": order_id}
    )

    if "Item" not in orders_response:
        raise HTTPException(status_code=404, detail="Order not found")

    order = Order(**orders_response.get("Item"))
    response = GetOrderResponse(**order.clean())
    return fastapi_gateway_response(200, {}, response.clean())
