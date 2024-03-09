import boto3
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from aws_lambda_powertools import Logger
from .models import Dessert

logger = Logger()
router = APIRouter()
client = boto3.client("dynamodb")


@logger.inject_lambda_context
@router.get(
    "/desserts/{uid}",
    status_code=200,
)
def get_dessert(uid):
    logger.info(f"Getting dessert with uid {uid}")
    dynamo_response = client.get_item(TableName="desserts", Key={"uid": {"S": uid}})

    if "Item" not in dynamo_response:
        raise HTTPException(status_code=404, detail="Dessert not found")

    dessert = dynamo_response.get("Item")
    dessert = Dessert(**dessert).clean()
    return {"dessert": dessert}
