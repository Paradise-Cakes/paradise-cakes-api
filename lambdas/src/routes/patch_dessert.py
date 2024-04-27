import os
import arrow
from boto3.dynamodb.conditions import Attr
from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException
from aws_lambda_powertools import Logger
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from src.lib.response import fastapi_gateway_response
from src.models import (
    Dessert,
    PatchDessertRequest,
)
from src.lib.dynamodb import DynamoConnection, update_attributes_expression

logger = Logger()
router = APIRouter()

desserts_table = DynamoConnection(
    os.environ.get("DYNAMODB_REGION", "us-east-1"),
    os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    os.environ.get("DYNAMODB_DESSERTS_TABLE_NAME", "desserts"),
).table


class PatchDessertResponse(Dessert):
    pass


@logger.inject_lambda_context(log_event=True)
@router.patch(
    "/desserts/{dessert_id}",
    status_code=200,
    response_model=PatchDessertResponse,
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

    if "prices" in updated_dessert:
        updated_dessert["prices"] = [
            {
                **price,
                "base": Decimal(price["base"]).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                ),
            }
            for price in updated_dessert["prices"]
        ]
        # TODO: FIGURE OUT HOW TO DO THIS IN A CLEANER WAY

    update_response = desserts_table.update_item(
        Key={"dessert_id": dessert_id},
        ReturnValues="ALL_NEW",
        **update_attributes_expression(updated_dessert),
    )

    response = PatchDessertResponse(**update_response["Attributes"])
    logger.info(f"Updated dessert: {response}")
    return fastapi_gateway_response(200, {}, response.clean())
