import boto3
from fastapi import APIRouter
from aws_lambda_powertools import Logger
from fastapi.exceptions import HTTPException
from src.models import Dessert


logger = Logger()
router = APIRouter()
client = boto3.client("dynamodb")


@logger.inject_lambda_context
@router.get(
    "/desserts",
    status_code=200,
)
def get_desserts():
    logger.info(f"Getting desserts")
    dynamo_response = client.scan(TableName="desserts")

    if "Items" not in dynamo_response:
        raise HTTPException(status_code=404, detail="No desserts found")

    desserts = [Dessert(**d).clean() for d in dynamo_response.get("Items")]

    logger.info(f"Returning {len(desserts)} desserts")
    return {"desserts": desserts}
