import os

import arrow
from aws_lambda_powertools import Logger
from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException

from src.lib.dynamodb import DynamoConnection, update_attributes_expression
from src.lib.response import fastapi_gateway_response
from src.models import Order, PatchOrderRequest

logger = Logger()
router = APIRouter()

orders_table = DynamoConnection(
    os.environ.get("DYNAMODB_REGION", "us-east-1"),
    os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    os.environ.get("DYNAMODB_ORDERS_TABLE_NAME", "orders"),
).table


class PatchOrderResponse(Order):
    pass


@logger.inject_lambda_context(log_event=True)
@router.patch(
    "/orders/{order_id}",
    status_code=200,
    response_model=PatchOrderResponse,
    tags=["Orders"],
)
def patch_order(request: Request, body: PatchOrderRequest, order_id: str):
    logger.info("Updating order")

    get_order_response = orders_table.get_item(Key={"order_id": order_id})
    if "Item" not in get_order_response:
        raise HTTPException(status_code=404, detail="Order not found")

    updated_order = {
        **body.model_dump(exclude_unset=True),
        "last_updated_at": int(arrow.utcnow().timestamp()),
    }

    update_response = orders_table.update_item(
        Key={"order_id": order_id},
        ReturnValues="ALL_NEW",
        **update_attributes_expression(updated_order),
    )

    response = PatchOrderResponse(**update_response["Attributes"])
    logger.info("Order updated successfully")
    return fastapi_gateway_response(200, {}, response.clean())
