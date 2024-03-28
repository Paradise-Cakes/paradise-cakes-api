import boto3
import os
from fastapi import APIRouter, Form, HTTPException
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger
from src.lib.response import fastapi_gateway_response

logger = Logger()
router = APIRouter()

cognito_client = boto3.client("cognito-idp", region_name="us-east-1")


@logger.inject_lambda_context(log_event=True)
@router.post("/resend_confirmation_code", status_code=200)
def post_resend_confirmation_code(email: str = Form(...)):
    logger.info(f"Resending confirmation code to user with email {email}")
    try:
        response = cognito_client.resend_confirmation_code(
            ClientId=os.environ.get("COGNITO_APP_CLIENT_ID"),
            Username=email,
        )
        return fastapi_gateway_response(
            200, {}, {"message": "Confirmation code resent", **response}
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "UserNotFoundException":
            raise HTTPException(status_code=400, detail="User not found")
        if e.response["Error"]["Code"] == "LimitExceededException":
            raise HTTPException(
                status_code=400, detail="Limit exceeded, please try again later"
            )
        raise HTTPException(status_code=400, detail=str(e))
