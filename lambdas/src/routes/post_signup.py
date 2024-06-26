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
@router.post("/signup", status_code=201)
def post_signup(
    email: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
):
    logger.info(f"Creating user with email {email}")

    try:
        response = cognito_client.sign_up(
            ClientId=os.environ.get("COGNITO_APP_CLIENT_ID"),
            Username=email,
            Password=password,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "given_name", "Value": first_name},
                {"Name": "family_name", "Value": last_name},
            ],
        )
        return fastapi_gateway_response(
            201,
            {},
            {
                "message": "User created",
                "given_name": first_name,
                "family_name": last_name,
                **response,
            },
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "UsernameExistsException":
            raise HTTPException(
                status_code=400, detail="User already exists with that email"
            )
        raise HTTPException(status_code=400, detail=str(e))
