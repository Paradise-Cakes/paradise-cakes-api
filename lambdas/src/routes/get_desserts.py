import boto3
from fastapi import APIRouter
from aws_lambda_powertools import Logger

logger = Logger()
router = APIRouter()
client = boto3.client("dynamodb")

@logger.inject_lambda_context
@router.get(
    "/desserts",
    status_code=200,
)
def get_desserts():
  logger.info("Getting desserts")
  response = client.scan(TableName="desserts")
  return response["Items"]