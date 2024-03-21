import boto3
import os
import arrow
from fastapi import APIRouter, Request
from aws_lambda_powertools import Logger
from src.lib.response import fastapi_gateway_response
from src.models import (
    Order,
    PostOrderRequest,
)
from src.lib.dynamodb import DynamoConnection

logger = Logger()
router = APIRouter()

orders_dynamodb_table = DynamoConnection(
    region_name=os.environ.get("DYNAMODB_REGION", "us-east-1"),
    endpoint_url=os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    table_name=os.environ.get("DYNAMODB_ORDERS_TABLE_NAME", "orders"),
).table

order_type_count_table = DynamoConnection(
    region_name=os.environ.get("DYNAMODB_REGION", "us-east-1"),
    endpoint_url=os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    table_name=os.environ.get(
        "DYNAMODB_ORDER_TYPE_COUNT_TABLE_NAME", "order_type_count"
    ),
).table


class PostOrderResponse(Order):
    pass


@logger.inject_lambda_context
@router.post(
    "/orders",
    status_code=201,
    response_model=PostOrderResponse,
)
def post_order(request: Request, body: PostOrderRequest):
    logger.info("Incrementing order type counter")
    order_type = "ORDER"
    get_response = order_type_count_table.get_item(Key={"order_type": order_type})

    if "Item" not in get_response:
        order_count = 1
        order_type_count_table.put_item(
            Item={"order_type": order_type, "order_count": order_count}
        )
    else:
        counter_response = order_type_count_table.update_item(
            Key={"order_type": "ORDER"},
            UpdateExpression="set order_count = order_count + :incr",
            ExpressionAttributeValues={":incr": 1},
            ReturnValues="ALL_NEW",
        )
        logger.info(counter_response)
        order_count = counter_response.get("Attributes").get("order_count")

    order_id = f"{order_type}-{order_count}"
    logger.info(f"Creating new order for {order_id}")

    new_order = Order(
        order_id=order_id,
        order_status="NEW",
        order_date=int(arrow.utcnow().timestamp()),
        **body.clean(),
    )

    orders_dynamodb_table.put_item(Item={**new_order.clean()})
    response = PostOrderResponse(**new_order.model_dump())
    logger.info(f"Created new order: {new_order}")
    return fastapi_gateway_response(201, {}, response.clean())
