import os
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from aws_lambda_powertools import Logger
from src.models import Dessert
from src.lib.dynamodb import DynamoConnection

import boto3
import fastapi
import fastapi.exceptions
import aws_lambda_powertools

logger = Logger()
router = APIRouter()

dynamodb_table = DynamoConnection(
    os.environ.get("DYNAMODB_REGION", "us-east-1"),
    os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    os.environ.get("DYNAMODB_DESSERTS_TABLE_NAME", "desserts"),
).table


@logger.inject_lambda_context
@router.get(
    "/desserts/{uid}",
    status_code=200,
)
def get_dessert(uid: str):
    logger.info(f"Getting dessert with uid {uid}")
    dynamo_response = dynamodb_table.get_item(
        TableName="desserts", Key={"uid": {"S": uid}}
    )

    if "Item" not in dynamo_response:
        raise HTTPException(status_code=404, detail="Dessert not found")

    dessert = dynamo_response.get("Item")
    dessert = Dessert(**dessert).clean()
    return {"dessert": dessert}
