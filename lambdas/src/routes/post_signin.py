import os
import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Form, HTTPException
from aws_lambda_powertools import Logger
from src.lib.response import fastapi_gateway_response

logger = Logger()
router = APIRouter()

cognito_client = boto3.client("cognito-idp", region_name="us-east-1")


@logger.inject_lambda_context(log_event=True)
@router.post("/signin", status_code=200)
def post_signin(email: str = Form(...), password: str = Form(...)):
    try:
        response = cognito_client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": email, "PASSWORD": password},
            ClientId=os.environ.get("COGNITO_APP_CLIENT_ID"),
        )
        return fastapi_gateway_response(200, {}, response)
    except ClientError as e:
        if (
            e.response["Error"]["Code"] == "UserNotFoundException"
            or e.response["Error"]["Code"] == "NotAuthorizedException"
        ):
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        raise HTTPException(status_code=400, detail=str(e))
