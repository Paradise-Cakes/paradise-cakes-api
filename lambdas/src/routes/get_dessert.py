import os
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from aws_lambda_powertools import Logger
from src.models import Dessert
from src.lib.dynamodb import DynamoConnection
from src.lib.response import fastapi_gateway_response

logger = Logger()
router = APIRouter()

desserts_table = DynamoConnection(
    os.environ.get("DYNAMODB_REGION", "us-east-1"),
    os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    os.environ.get("DYNAMODB_DESSERTS_TABLE_NAME", "desserts"),
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
    dynamo_response = desserts_table.get_item(
        TableName="desserts", Key={"dessert_id": dessert_id}
    )

    if "Item" not in dynamo_response:
        raise HTTPException(status_code=404, detail="Dessert not found")

    dessert = Dessert(**dynamo_response.get("Item"))
    response = GetDessertResponse(**dessert.clean())
    return fastapi_gateway_response(200, {}, response.clean())
