import os
from datetime import datetime, timezone
from decimal import Decimal

import arrow
import boto3
from aws_lambda_powertools import Logger
from fastapi import APIRouter, Request

from src.lib.dynamodb import DynamoConnection
from src.lib.response import fastapi_gateway_response
from src.models import Order, PostOrderRequest

MAX_ORDERS_FOR_DAY = 2
MAX_DESSERT_QUANTITY = 2

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

prices_table = DynamoConnection(
    region_name=os.environ.get("DYNAMODB_REGION", "us-east-1"),
    endpoint_url=os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    table_name=os.environ.get("DYNAMODB_PRICES_TABLE_NAME", "prices"),
).table


class PostOrderResponse(Order):
    pass


class OrderLimitExceededException(Exception):
    pass


class DessertLimitExceededException(Exception):
    pass


def calculate_order_total(desserts):
    logger.info("Calculating order total")
    total = Decimal("0.00")
    for dessert in desserts:
        dessert_id = dessert.dessert_id
        size = dessert.size
        quantity = dessert.quantity

        response = prices_table.get_item(Key={"dessert_id": dessert_id, "size": size})
        if "Item" in response:
            price = Decimal(response.get("Item").get("base_price")) - Decimal(
                response.get("Item").get("discount")
            )
            total += price * quantity

    return total


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
    responses={
        201: {
            "description": "Successfully created order",
            "content": {
                "application/json": {
                    "example": {
                        "order_id": "ORDER-2",
                        "customer_first_name": "Anthony",
                        "customer_last_name": "Soprano",
                        "customer_full_name": "Anthony Soprano",
                        "customer_email": "anthony.soprano@gmail.com",
                        "customer_phone_number": "555-555-5555",
                        "delivery_zip_code": "07001",
                        "delivery_address_line_1": "123 Main St",
                        "delivery_address_line_2": "Apt 1",
                        "delivery_date": "12-12-2024",
                        "delivery_time": 1734004800,
                        "order_status": "NEW",
                        "order_date": "12-12-2024",
                        "order_time": 1734004800,
                        "approved": False,
                        "custom_order": False,
                        "order_total": 0.00,
                        "desserts": [
                            {
                                "dessert_id": "SCHEMA-TEST-DESSERT-ID",
                                "dessert_name": "Lemon Blueberry Cake",
                                "size": "6 inch",
                                "quantity": 2,
                            }
                        ],
                    }
                }
            },
        },
        400: {
            "description": "Order Limit Exceeded Error",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Order limit exceeded for date: 01-01-2022. Max orders: 2"
                    }
                }
            },
        },
    },
    tags=["Orders"],
)
def post_order(request: Request, body: PostOrderRequest):
    logger.info("checking if order limit has been exceeded")
    order_type = "ORDER"

    # are there more than two orders for this date?
    try:
        new_order = Order(
            **body.clean(),
            order_id="",
            order_date=datetime.now().strftime("%m-%d-%Y"),
            order_time=int(datetime.now().timestamp()),
            order_total=0.00,
            customer_full_name=f"{body.customer_first_name} {body.customer_last_name}",
            last_updated_at=int(arrow.utcnow().timestamp()),
        )

        new_order_delivery_date = new_order.delivery_date

        orders_for_date = count_orders_for_date(new_order_delivery_date)
        if orders_for_date >= MAX_ORDERS_FOR_DAY:
            raise OrderLimitExceededException(
                f"Order limit exceeded for date: {new_order_delivery_date}. Max orders: {MAX_ORDERS_FOR_DAY}"
            )

        for dessert in new_order.desserts:
            if dessert.quantity > MAX_DESSERT_QUANTITY:
                raise DessertLimitExceededException(
                    f"Dessert quantity limit exceeded for dessert: {dessert.dessert_id}. Max quantity: {MAX_DESSERT_QUANTITY}"
                )

        logger.info("Incrementing order type counter")
        order_type_count_response = order_type_count_table.get_item(
            Key={"order_type": order_type}
        )

        if "Item" not in order_type_count_response:
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
        new_order.order_total = calculate_order_total(new_order.desserts)

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

    except DessertLimitExceededException as e:
        logger.error(e)
        return fastapi_gateway_response(400, {}, {"error": str(e)})
