import email as email_reader
import imaplib
import os
import re
import time
import uuid
from datetime import datetime, timezone

import boto3
import pytest
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from request_helper import RequestHelper

from lib.auth_utils import get_user_confirmation_code_from_email

load_dotenv()


@pytest.fixture(scope="session")
def api_url():
    local_port = os.getenv("LOCAL_PORT")

    if local_port:
        return f"http://localhost:{local_port}"

    return "https://dev-api.megsparadisecakes.com"


@pytest.fixture(scope="session")
def request_helper(api_url):
    return RequestHelper(api_url, {})


@pytest.fixture(scope="session")
def dynamodb_client():
    return boto3.client("dynamodb", region_name="us-east-1")


@pytest.fixture(scope="session")
def cognito_client():
    return boto3.client("cognito-idp", region_name="us-east-1")


@pytest.fixture(scope="function")
def email_client():
    email = os.environ.get("DEV_TEST_EMAIL")
    password = os.environ.get("DEV_TEST_EMAIL_PASSWORD")

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email, password)
    mail.select("inbox")

    return {"client": mail, "email": email}


@pytest.fixture(scope="function")
def function_signup(cognito_client, cleanup_cognito_users):
    email = os.environ.get("DEV_TEST_EMAIL")
    password = os.getenv("DEV_EMAIL_PASSWORD")

    cognito_client.sign_up(
        ClientId=os.environ.get("COGNITO_APP_CLIENT_ID"),
        Username=email,
        Password=password,
        UserAttributes=[
            {"Name": "email", "Value": email},
            {"Name": "given_name", "Value": "John"},
            {"Name": "family_name", "Value": "Cena"},
        ],
    )
    cleanup_cognito_users.append(email)

    return {"email": email, "password": password}


@pytest.fixture(scope="function")
def function_signup_and_verification_code(email_client, function_signup):
    mail_client = email_client["client"]
    email = function_signup["email"]
    password = function_signup["password"]

    confirmation_code = get_user_confirmation_code_from_email(
        mail_client, "Welcome to Paradise Cakes!", "Your verification code is:"
    )

    return {
        "email": email,
        "password": password,
        "confirmation_code": confirmation_code,
    }


@pytest.fixture(scope="function")
def function_confirmed_account(
    cognito_client,
    function_signup_and_verification_code,
):
    email = function_signup_and_verification_code["email"]
    confirmation_code = function_signup_and_verification_code["confirmation_code"]

    cognito_client.confirm_sign_up(
        ClientId=os.environ.get("COGNITO_APP_CLIENT_ID"),
        Username=email,
        ConfirmationCode=confirmation_code,
    )

    return {"email": email}


@pytest.fixture(scope="function")
def function_forgot_password_code(
    email_client, cognito_client, function_confirmed_account
):
    mail_client = email_client["client"]
    email = function_confirmed_account["email"]

    cognito_client.forgot_password(
        ClientId=os.environ.get("COGNITO_APP_CLIENT_ID"), Username=email
    )

    reset_code = get_user_confirmation_code_from_email(
        mail_client, "Reset Your Password", "Your reset code is:"
    )

    return {"email": email, "reset_code": reset_code}


@pytest.fixture(scope="function")
def function_prices(dynamodb_client, cleanup_prices):
    def _create_prices(dessert_id):
        records = [
            {
                "dessert_id": {"S": dessert_id},
                "size": {"S": "slice"},
                "base_price": {"N": "5.00"},
                "discount": {"N": "0.00"},
            },
            {
                "dessert_id": {"S": dessert_id},
                "size": {"S": "whole"},
                "base_price": {"N": "40.00"},
                "discount": {"N": "0.00"},
            },
        ]

        for record in records:
            dynamodb_client.put_item(
                TableName="prices",
                Item=record,
            )
        cleanup_prices.extend(records)

        return {"dessert_id": dessert_id, "records": records}

    return _create_prices


@pytest.fixture(scope="function")
def function_orders(dynamodb_client, cleanup_orders):
    order_ids = [
        f"ORDER-{str(uuid.uuid4())}",
        f"ORDER-{str(uuid.uuid4())}",
        f"ORDER-{str(uuid.uuid4())}",
    ]

    records = [
        {
            "order_id": {"S": order_ids[0]},
            "customer_first_name": {"S": "John"},
            "customer_last_name": {"S": "Cena"},
            "customer_full_name": {"S": "John Cena"},
            "customer_email": {"S": "john.cena@gmail.com"},
            "customer_phone_number": {"S": "1234567890"},
            "delivery_zip_code": {"S": "12345"},
            "delivery_address_line_1": {"S": "123 Main St"},
            "delivery_address_line_2": {"S": "Apt 1"},
            "delivery_date": {"S": "01-01-2022"},
            "delivery_time": {"N": "12"},
            "order_status": {"S": "NEW"},
            "order_date": {"S": "12-31-2021"},
            "order_time": {"N": "12"},
            "approved": {"BOOL": False},
            "custom_order": {"BOOL": False},
            "order_total": {"N": "0.00"},
            "desserts": {
                "L": [
                    {
                        "M": {
                            "dessert_id": {"S": "DESSERT-1"},
                            "dessert_name": {"S": "Chocolate Cake"},
                            "size": {"S": "slice"},
                            "quantity": {"N": "2"},
                        }
                    }
                ]
            },
            "last_updated_at": {"N": "1734036429"},
        },
        {
            "order_id": {"S": order_ids[1]},
            "customer_first_name": {"S": "Jane"},
            "customer_last_name": {"S": "Doe"},
            "customer_full_name": {"S": "Jane Doe"},
            "customer_email": {"S": "jane.doe@gmail.com"},
            "customer_phone_number": {"S": "0987654321"},
            "delivery_zip_code": {"S": "54321"},
            "delivery_address_line_1": {"S": "456 Elm St"},
            "delivery_address_line_2": {"S": "Apt 2"},
            "delivery_date": {"S": "02-02-2022"},
            "delivery_time": {"N": "14"},
            "order_status": {"S": "NEW"},
            "order_date": {"S": "01-02-2022"},
            "order_time": {"N": "14"},
            "approved": {"BOOL": False},
            "custom_order": {"BOOL": False},
            "order_total": {"N": "0.00"},
            "desserts": {
                "L": [
                    {
                        "M": {
                            "dessert_id": {"S": "DESSERT-2"},
                            "dessert_name": {"S": "Cheesecake"},
                            "size": {"S": "whole"},
                            "quantity": {"N": "1"},
                        }
                    }
                ]
            },
            "last_updated_at": {"N": "1734036429"},
        },
        {
            "order_id": {"S": order_ids[2]},
            "customer_first_name": {"S": "James"},
            "customer_last_name": {"S": "Bond"},
            "customer_full_name": {"S": "James Bond"},
            "customer_email": {"S": "james.bond@gmail.com"},
            "customer_phone_number": {"S": "1357924680"},
            "delivery_zip_code": {"S": "67890"},
            "delivery_address_line_1": {"S": "789 Oak St"},
            "delivery_address_line_2": {"S": "Apt 3"},
            "delivery_date": {"S": "03-02-2023"},
            "delivery_time": {"N": "16"},
            "order_status": {"S": "NEW"},
            "order_date": {"S": "03-02-2023"},
            "order_time": {"N": "16"},
            "approved": {"BOOL": False},
            "custom_order": {"BOOL": False},
            "order_total": {"N": "0.00"},
            "desserts": {
                "L": [
                    {
                        "M": {
                            "dessert_id": {"S": "DESSERT-3"},
                            "dessert_name": {"S": "Carrot Cake"},
                            "size": {"S": "slice"},
                            "quantity": {"N": "3"},
                        }
                    }
                ]
            },
            "last_updated_at": {"N": "1734036429"},
        },
    ]

    cleanup_orders.extend(order_ids)

    for record in records:
        dynamodb_client.put_item(
            TableName="orders",
            Item=record,
        )

    return {"order_ids": order_ids, "records": records}


@pytest.fixture(scope="function")
def function_order(dynamodb_client, cleanup_orders):
    def _get_order_record(delivery_date="01-01-2022"):
        order_id = f"ORDER-{str(uuid.uuid4())}"

        record = {
            "order_id": {"S": order_id},
            "customer_first_name": {"S": "John"},
            "customer_last_name": {"S": "Cena"},
            "customer_full_name": {"S": "John Cena"},
            "customer_email": {"S": "john.cena@gmail.com"},
            "customer_phone_number": {"S": "1234567890"},
            "delivery_zip_code": {"S": "12345"},
            "delivery_address_line_1": {"S": "123 Main St"},
            "delivery_address_line_2": {"S": "Apt 1"},
            "delivery_date": {"S": delivery_date},
            "delivery_time": {"N": "12"},
            "order_status": {"S": "NEW"},
            "order_date": {"S": "12-31-2021"},
            "order_time": {"N": "12"},
            "approved": {"BOOL": False},
            "custom_order": {"BOOL": False},
            "order_total": {"N": "0.00"},
            "desserts": {
                "L": [
                    {
                        "M": {
                            "dessert_id": {"S": "DESSERT-1"},
                            "dessert_name": {"S": "Chocolate Cake"},
                            "size": {"S": "slice"},
                            "quantity": {"N": "2"},
                        }
                    }
                ]
            },
            "last_updated_at": {"N": "1734036429"},
        }

        dynamodb_client.put_item(
            TableName="orders",
            Item=record,
        )

        cleanup_orders.append(order_id)

        return {"order_id": order_id, "record": record}

    return _get_order_record


@pytest.fixture(scope="function")
def function_dessert(dynamodb_client, cleanup_desserts):
    dessert_id = f"DESSERT-{str(uuid.uuid4())}"

    record = {
        "dessert_id": {"S": dessert_id},
        "name": {"S": "Chocolate Cake"},
        "description": {"S": "its a chocolate cake"},
        "dessert_type": {"S": "cake"},
        "created_at": {"N": f"{int(datetime.now(tz=timezone.utc).timestamp())}"},
        "last_updated_at": {"N": f"{int(datetime.now(tz=timezone.utc).timestamp())}"},
        "visible": {"BOOL": False},
        "prices": {
            "L": [
                {
                    "M": {
                        "dessert_id": {"S": dessert_id},
                        "size": {"S": "slice"},
                        "base_price": {"N": "5.00"},
                        "discount": {"N": "0.00"},
                    }
                },
                {
                    "M": {
                        "dessert_id": {"S": dessert_id},
                        "size": {"S": "whole"},
                        "base_price": {"N": "40.00"},
                        "discount": {"N": "0.00"},
                    }
                },
            ]
        },
        "ingredients": {
            "L": [
                {"S": "flour"},
                {"S": "sugar"},
                {"S": "cocoa"},
                {"S": "butter"},
                {"S": "eggs"},
            ]
        },
        "images": {
            "L": [
                {
                    "M": {
                        "image_id": {"S": "IMAGE-1"},
                        "url": {"S": "https://example.com/image1.jpg"},
                        "upload_url": {"S": "https://example.com/upload-url"},
                        "position": {"N": "1"},
                        "file_name": {"S": "image1.jpg"},
                        "file_type": {"S": "jpg"},
                    }
                },
                {
                    "M": {
                        "image_id": {"S": "IMAGE-2"},
                        "url": {"S": "https://example.com/image2.jpg"},
                        "upload_url": {"S": "https://example.com/upload-url"},
                        "position": {"N": "2"},
                        "file_name": {"S": "image2.jpg"},
                        "file_type": {"S": "jpg"},
                    }
                },
            ]
        },
    }

    dynamodb_client.put_item(
        TableName="desserts",
        Item=record,
    )

    dynamodb_client.batch_write_item(
        RequestItems={
            "prices": [
                {
                    "PutRequest": {
                        "Item": {
                            "dessert_id": {"S": dessert_id},
                            "size": {"S": "slice"},
                            "base_price": {"N": "5.00"},
                            "discount": {"N": "0.00"},
                        }
                    }
                },
                {
                    "PutRequest": {
                        "Item": {
                            "dessert_id": {"S": dessert_id},
                            "size": {"S": "whole"},
                            "base_price": {"N": "40.00"},
                            "discount": {"N": "0.00"},
                        }
                    }
                },
            ]
        }
    )
    cleanup_desserts.append(dessert_id)

    return {"dessert_id": dessert_id, "record": record}


@pytest.fixture(scope="function")
def cleanup_orders(dynamodb_client):
    orders_to_cleanup = []
    yield orders_to_cleanup

    # Cleanup logic
    for order_id in orders_to_cleanup:
        try:
            dynamodb_client.delete_item(
                Key={
                    "order_id": {"S": order_id},
                },
                TableName="orders",
            )
            print(f"Deleted test order: {order_id}")
        except Exception as e:
            print(f"Failed to delete order {order_id}: {e}")
            raise e


@pytest.fixture(scope="function")
def cleanup_desserts(dynamodb_client):
    desserts_to_cleanup = []
    yield desserts_to_cleanup

    # Cleanup logic
    for dessert_id in desserts_to_cleanup:
        try:
            dessert_prices = dynamodb_client.query(
                TableName="prices",
                KeyConditionExpression="dessert_id = :dessert_id",
                ExpressionAttributeValues={":dessert_id": {"S": dessert_id}},
            )
            for price in dessert_prices.get("Items"):
                dynamodb_client.delete_item(
                    Key={
                        "dessert_id": {"S": dessert_id},
                        "size": price.get("size"),
                    },
                    TableName="prices",
                )
            print(f"Deleted test dessert prices: {dessert_id}")
            dynamodb_client.delete_item(
                Key={
                    "dessert_id": {"S": dessert_id},
                },
                TableName="desserts",
            )
            print(f"Deleted test dessert: {dessert_id}")
        except Exception as e:
            print(f"Failed to delete dessert {dessert_id}: {e}")
            raise e


@pytest.fixture(scope="function")
def cleanup_prices(dynamodb_client):
    prices_to_cleanup = []
    yield prices_to_cleanup

    for price in prices_to_cleanup:
        dessert_id = price.get("dessert_id").get("S")
        size = price.get("size").get("S")
        try:
            dynamodb_client.delete_item(
                Key={
                    "dessert_id": {"S": dessert_id},
                    "size": {"S": size},
                },
                TableName="prices",
            )
            print(f"Deleted test price: {dessert_id} - {size}")
        except Exception as e:
            print(f"Failed to delete price {dessert_id} - {size}: {e}")
            raise e


@pytest.fixture(scope="function")
def cleanup_cognito_users(cognito_client):
    users_to_cleanup = []
    yield users_to_cleanup

    for email in users_to_cleanup:
        try:
            cognito_client.admin_delete_user(
                UserPoolId=os.getenv("DEV_USER_POOL_ID"),
                Username=email,
            )
            print(f"Deleted test user: {email}")
        except Exception as e:
            print(f"Failed to delete user {email}: {e}")
            raise e
