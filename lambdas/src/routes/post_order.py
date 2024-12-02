import boto3
import os
import arrow
from decimal import Decimal
from fastapi import APIRouter, Request
from aws_lambda_powertools import Logger
from src.lib.response import fastapi_gateway_response
from src.models import (
    Order,
    PostOrderRequest,
)
from src.lib.dynamodb import DynamoConnection
from datetime import datetime, timezone

MAX_ORDERS_FOR_DAY = 2

logger = Logger()
router = APIRouter()

orders_table = DynamoConnection(
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


class OrderLimitExceededException(Exception):
    pass


def count_orders_for_date(delivery_date):
    response = orders_table.query(
        IndexName="delivery_date_index",
        KeyConditionExpression="delivery_date = :date",
        ExpressionAttributeValues={":date": delivery_date},
    )

    return len(response["Items"])


@logger.inject_lambda_context(log_event=True)
@router.post(
    "/orders",
    status_code=201,
    response_model=PostOrderResponse,
)
def post_order(request: Request, body: PostOrderRequest):
    logger.info("checking if order limit has been exceeded")
    order_type = "ORDER"

    # are there more than two orders for this date?
    try:
        new_order = Order(
            **body.clean(),
            order_id="",
            order_status="NEW",
            order_date=int(arrow.utcnow().timestamp()),
        )

        new_order_delivery_date = new_order.delivery_date

        orders_for_date = count_orders_for_date(new_order_delivery_date)
        if orders_for_date >= MAX_ORDERS_FOR_DAY:
            raise OrderLimitExceededException(
                f"Order limit exceeded for {new_order_delivery_date}. Max orders: {MAX_ORDERS_FOR_DAY}"
            )

        logger.info("Incrementing order type counter")
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
        new_order.order_id = order_id

        logger.info(f"Creating new order for {order_id}")

        if new_order.custom_order:
            orders_table.put_item(Item={**new_order.clean()})
        else:
            orders_table.put_item(
                Item={
                    **new_order.clean(),
                    "order_total": Decimal(str(new_order.order_total)),
                }
            )

        response = PostOrderResponse(**new_order.model_dump())
        logger.info(f"Created new order: {new_order}")
        return fastapi_gateway_response(201, {}, response.clean())

    except OrderLimitExceededException as e:
        logger.error(e)
        return fastapi_gateway_response(400, {}, {"error": str(e)})
