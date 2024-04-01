import boto3
import os
import arrow
from decimal import Decimal
from fastapi import APIRouter, Request
from aws_lambda_powertools import Logger
from src.lib.response import fastapi_gateway_response
from src.models import (
    Dessert,
    PostDessertRequest,
)
from src.lib.dynamodb import DynamoConnection

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
    dessert_id = arrow.utcnow().timestamp
    body.dessert_id = str(dessert_id)
    body.prices = [p.dict() for p in body.prices]
    body.image_urls = [i.dict() for i in body.image_urls]
    body.ingredients = body.ingredients

    desserts_table.put_item(Item=body.dict())
    logger.info(f"Created dessert {dessert_id}")
    return fastapi_gateway_response(201, {}, body.dict())