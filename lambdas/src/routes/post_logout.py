import os
import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Response, Form, HTTPException, Request
from aws_lambda_powertools import Logger
from src.lib.response import fastapi_gateway_response

logger = Logger()
router = APIRouter()

cognito_client = boto3.client("cognito-idp", region_name="us-east-1")


def global_post_logout(access_token):
    try:
        cognito_client.global_sign_out(AccessToken=access_token)
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))


@logger.inject_lambda_context(log_event=True)
@router.post("/logout", status_code=200)
def post_logout(response: Response, request: Request):
    access_token = request.cookies.get("access_token")
    if access_token:
        global_post_logout(access_token)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return fastapi_gateway_response(
        200, {}, {"message": "User logged out successfully"}
    )
