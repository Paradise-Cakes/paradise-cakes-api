import os
import uuid
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

import arrow
from aws_lambda_powertools import Logger
from fastapi import APIRouter, Request

from src.lib.dynamodb import DynamoConnection
from src.lib.response import fastapi_gateway_response
from src.models import Dessert, PostDessertRequest

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
    formatted_prices = [
        {
            "dessert_id": new_dessert.dessert_id,
            "size": price.size,
            "base_price": Decimal(price.base_price).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
            "discount": Decimal(price.discount).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
        }
        for price in new_dessert.prices
    ]
    new_dessert.prices = formatted_prices
    with prices_table.batch_writer() as batch:
        for price in formatted_prices:
            batch.put_item(Item=price)

    desserts_table.put_item(Item={**new_dessert.clean()})
    response = PostDessertResponse(**new_dessert.model_dump())

    logger.info(f"Created new dessert: {new_dessert}")
    return fastapi_gateway_response(201, {}, response.clean())
