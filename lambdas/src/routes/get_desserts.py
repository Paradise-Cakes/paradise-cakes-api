import os

import boto3
from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeDeserializer
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from src.lib.dynamodb import DynamoConnection
from src.lib.response import fastapi_gateway_response
from src.models import Dessert

logger = Logger()
router = APIRouter()

dynamodb_client = boto3.client("dynamodb", "us-east-1")

desserts_table = DynamoConnection(
    os.environ.get("DYNAMODB_REGION", "us-east-1"),
    os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    os.environ.get("DYNAMODB_DESSERTS_TABLE_NAME", "desserts"),
).table


@logger.inject_lambda_context(log_event=True)
@router.get(
    "/desserts",
    status_code=200,
)
def get_desserts(dessert_type: str):
    logger.info(f"Getting desserts of type {dessert_type}")

    desserts_response = desserts_table.query(
        IndexName="dessert_type_index",
        KeyConditionExpression=Key("dessert_type").eq(dessert_type),
    )

    if not desserts_response.get("Items"):
        raise HTTPException(
            status_code=404, detail=f"No desserts found of type {dessert_type}"
        )

    dessert_ids = [d["dessert_id"] for d in desserts_response.get("Items")]

    prices_response = dynamodb_client.batch_get_item(
        RequestItems={
            "prices": {
                "Keys": [
                    {"dessert_id": {"S": dessert_id}} for dessert_id in dessert_ids
                ]
            }
        }
    )

    prices = prices_response.get("Responses").get("prices")
    deserializer = TypeDeserializer()
    deserialized_prices = [
        {k: deserializer.deserialize(v) for k, v in price.items()} for price in prices
    ]

    for dessert in desserts_response.get("Items"):
        dessert["prices"] = [
            p
            for p in deserialized_prices
            if p.get("dessert_id") == dessert.get("dessert_id")
        ]

    desserts = [Dessert(**d).clean() for d in desserts_response.get("Items")]

    return fastapi_gateway_response(200, {}, desserts)
