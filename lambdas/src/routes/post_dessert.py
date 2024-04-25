import os
import arrow
from fastapi import APIRouter, Request
from aws_lambda_powertools import Logger
from decimal import Decimal, ROUND_HALF_UP
from src.lib.response import fastapi_gateway_response
from datetime import datetime
from src.models import (
    Dessert,
    PostDessertRequest,
)
from src.lib.dynamodb import DynamoConnection
import uuid

logger = Logger()
router = APIRouter()

desserts_table = DynamoConnection(
    os.environ.get("DYNAMODB_REGION", "us-east-1"),
    os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    os.environ.get("DYNAMODB_DESSERTS_TABLE_NAME", "desserts"),
).table


class PostDessertResponse(Dessert):
    pass


@logger.inject_lambda_context(log_event=True)
@router.post(
    "/desserts",
    status_code=201,
    response_model=PostDessertResponse,
)
def post_dessert(request: Request, body: PostDessertRequest):
    logger.info("Creating new dessert")

    new_dessert = Dessert(
        **body.clean(),
        dessert_id=str(uuid.uuid4()),
        created_at=int(arrow.utcnow().timestamp()),
        last_updated_at=int(arrow.utcnow().timestamp()),
    )

    # TODO: FIGURE OUT HOW TO DO THIS IN A CLEANER WAY
    new_prices = [
        {
            **price.clean(),
            "base": Decimal(price.base).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
        }
        for price in new_dessert.prices
    ]

    desserts_table.put_item(Item={**new_dessert.clean(), "prices": new_prices})
    response = PostDessertResponse(**new_dessert.model_dump())
    logger.info(f"Created new dessert: {new_dessert}")
    return fastapi_gateway_response(201, {}, response.clean())
