import boto3
from fastapi import APIRouter
from aws_lambda_powertools import Logger

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
  response = client.get_item(
    TableName="desserts",
    Key={"uid": {"S": uid}}
  )
  return response["Item"]