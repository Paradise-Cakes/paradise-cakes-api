import os

import boto3
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError
from fastapi import APIRouter, Form, HTTPException

from src.lib.response import fastapi_gateway_response

logger = Logger()
router = APIRouter()

cognito_client = boto3.client("cognito-idp", region_name="us-east-1")


@logger.inject_lambda_context(log_event=True)
@router.post("/confirm_forgot_password", status_code=200, tags=["Authentication"])
def post_confirm_forgot_password(
    email: str = Form(...), code: str = Form(...), password: str = Form(...)
):
    logger.info(f"Confirming password reset for email {email}")

    try:
        cognito_client.confirm_forgot_password(
            ClientId=os.environ.get("COGNITO_APP_CLIENT_ID"),
            Username=email,
            ConfirmationCode=code,
            Password=password,
        )
        return fastapi_gateway_response(
            200, {}, {"message": f"Password reset for {email} successful"}
        )
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))
