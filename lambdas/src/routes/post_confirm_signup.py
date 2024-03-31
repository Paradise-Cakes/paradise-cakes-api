from fastapi import APIRouter, Form, HTTPException, Response
import boto3
import os
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError
from src.lib.response import fastapi_gateway_response

logger = Logger()
router = APIRouter()

cognito_client = boto3.client("cognito-idp", region_name="us-east-1")


@logger.inject_lambda_context(log_event=True)
@router.post("/confirm_signup", status_code=200)
def post_confirm_signup(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    confirmation_code: str = Form(...),
):
    logger.info(f"Confirming user with email {email}")
    try:
        cognito_client.confirm_sign_up(
            ClientId=os.environ.get("COGNITO_APP_CLIENT_ID"),
            Username=email,
            ConfirmationCode=confirmation_code,
        )
        auth_response = cognito_client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": email, "PASSWORD": password},
            ClientId=os.environ.get("COGNITO_APP_CLIENT_ID"),
        )
        access_token = auth_response["AuthenticationResult"]["AccessToken"]
        refresh_token = auth_response["AuthenticationResult"]["RefreshToken"]
        expires_in = auth_response["AuthenticationResult"]["ExpiresIn"]

        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=expires_in,
            secure=False,
            httponly=True,
            samesite="strict",
        )

        refresh_token_expires_in = 30 * 24 * 60 * 60  # 30 days
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=refresh_token_expires_in,
            secure=False,
            httponly=True,
            samesite="strict",
        )

        return fastapi_gateway_response(
            200, {}, {"message": "User confirmed and signed in"}
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "CodeMismatchException":
            raise HTTPException(status_code=400, detail="Invalid confirmation code")
        if e.response["Error"]["Code"] == "ExpiredCodeException":
            raise HTTPException(status_code=400, detail="Confirmation code expired")
        raise HTTPException(status_code=400, detail=str(e))
