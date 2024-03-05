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
def get_desserts(type: str = None):
  logger.info(f"Getting desserts of type {type}")

  if type:
    response = client.query(
      TableName="desserts",
      IndexName="type",
      KeyConditionExpression="type = :type",
      ExpressionAttributeValues={":type": {"S": type}}
    )
  else:
    response = client.query(
      TableName="desserts",
      IndexName="uid",
    )
  return response["Items"]