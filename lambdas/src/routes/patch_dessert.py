import os
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

import arrow
from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Attr
from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException

from src.lib.dynamodb import DynamoConnection, update_attributes_expression
from src.lib.response import fastapi_gateway_response
from src.models import Dessert, PatchDessertRequest

logger = Logger()
router = APIRouter()

desserts_table = DynamoConnection(
    os.environ.get("DYNAMODB_REGION", "us-east-1"),
    os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    os.environ.get("DYNAMODB_DESSERTS_TABLE_NAME", "desserts"),
).table


prices_table = DynamoConnection(
    os.environ.get("DYNAMODB_REGION", "us-east-1"),
    os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    os.environ.get("DYNAMODB_PRICES_TABLE_NAME", "prices"),
).table


class PatchDessertResponse(Dessert):
    pass


@logger.inject_lambda_context(log_event=True)
@router.patch(
    "/desserts/{dessert_id}",
    status_code=200,
    response_model=PatchDessertResponse,
    tags=["Desserts"],
)
def patch_dessert(request: Request, body: PatchDessertRequest, dessert_id: str):
    logger.info("Updating dessert")

    get_dessert_response = desserts_table.get_item(Key={"dessert_id": dessert_id})
    if "Item" not in get_dessert_response:
        raise HTTPException(status_code=404, detail="Dessert not found")

    updated_dessert = {
        **body.model_dump(exclude_unset=True),
        "last_updated_at": int(arrow.utcnow().timestamp()),
    }

    # TODO: FIGURE OUT HOW TO DO THIS IN A CLEANER WAY
    if "prices" in updated_dessert:
        formatted_prices = [
            {
                "dessert_id": dessert_id,
                "size": price.get("size"),
                "base_price": Decimal(price.get("base_price")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                ),
                "discount": Decimal(price.get("discount")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                ),
            }
            for price in updated_dessert.get("prices", [])
        ]
        updated_dessert["prices"] = formatted_prices
        with prices_table.batch_writer() as batch:
            for price in formatted_prices:
                batch.put_item(Item=price)

    update_response = desserts_table.update_item(
        Key={"dessert_id": dessert_id},
        ReturnValues="ALL_NEW",
        **update_attributes_expression(updated_dessert),
    )

    response = PatchDessertResponse(**update_response["Attributes"])
    logger.info(f"Updated dessert: {response}")
    return fastapi_gateway_response(200, {}, response.clean())
