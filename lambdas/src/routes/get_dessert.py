import os

from aws_lambda_powertools import Logger
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from src.lib.dynamodb import DynamoConnection
from src.lib.response import fastapi_gateway_response
from boto3.dynamodb.conditions import Key
from src.models import Dessert

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


class GetDessertResponse(Dessert):
    pass


@logger.inject_lambda_context(log_event=True)
@router.get(
    "/desserts/{dessert_id}",
    status_code=200,
    response_model=GetDessertResponse,
)
def get_dessert(dessert_id: str):
    logger.info(f"Getting dessert with dessert_id {dessert_id}")

    desserts_response = desserts_table.get_item(
        TableName="desserts", Key={"dessert_id": dessert_id}
    )

    if "Item" not in desserts_response:
        raise HTTPException(status_code=404, detail="Dessert not found")

    # get me all the prices for this dessert
    prices_response = prices_table.query(
        KeyConditionExpression=Key("dessert_id").eq(dessert_id),
    )

    dessert = Dessert(
        **desserts_response.get("Item"), prices=prices_response.get("Items")
    )
    response = GetDessertResponse(**dessert.clean())
    return fastapi_gateway_response(200, {}, response.clean())
