from fastapi import APIRouter, Form, HTTPException
import boto3
import os
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError
from src.lib.response import fastapi_gateway_response

logger = Logger()
router = APIRouter()

cognito_client = boto3.client("cognito-idp", region_name="us-east-1")


@logger.inject_lambda_context
@router.post("/confirm_signup", status_code=200)
def post_confirm_signup(email: str = Form(...), confirmation_code: str = Form(...)):
    try:
        response = cognito_client.confirm_sign_up(
            ClientId=os.environ.get("COGNITO_APP_CLIENT_ID"),
            Username=email,
            ConfirmationCode=confirmation_code,
        )
        return fastapi_gateway_response(
            200, {}, {"message": "User confirmed", **response}
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "CodeMismatchException":
            raise HTTPException(status_code=400, detail="Invalid confirmation code")
        if e.response["Error"]["Code"] == "ExpiredCodeException":
            raise HTTPException(status_code=400, detail="Confirmation code expired")
        raise HTTPException(status_code=400, detail=str(e))
