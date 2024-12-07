import os
import pytest
import boto3
import uuid

from datetime import datetime, timezone
from request_helper import RequestHelper


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


@pytest.fixture(scope="function")
def function_order(dynamodb_client, quantity=1, custom_order=False):
    order_id = str(uuid.uuid4())

    records = [
        {
            "order_id": {"S": f"ORDER:{order_id}"},
            "dessert_id": {"S": "INT_TEST_DESSERT_ID"},
            "dessert_name": {"S": "INT_TEST_DESSERT_NAME"},
            "quantity": {"N": f"{quantity}"},
            "customer_first_name": {"S": "INT_TEST_FIRST_NAME"},
            "customer_last_name": {"S": "INT_TEST_LAST_NAME"},
            "customer_email": {"S": "INT_TEST_EMAIL"},
            "customer_phone_number": {"S": "INT_TEST_PHONE_NUMBER"},
            "delivery_zip_code": {"S": "INT_TEST_ZIP_CODE"},
            "delivery_address_line_1": {"S": "INT_TEST_ADDRESS_LINE_1"},
            "delivery_address_line_2": {"S": "INT_TEST_ADDRESS_LINE_2"},
            "delivery_date": {"S": "12-12-2024"},
            "delivery_time": {"N": "1711108800"},
            "order_total": {"N": "0.00"},
            "order_status": {"S": "pending"},
            "order_date": {"N": f"{int(datetime.now(tz=timezone.utc).timestamp())}"},
            "description": {"S": "INT_TEST_DESCRIPTION"},
            "custom_order": {"BOOL": custom_order},
        }
    ]

    for record in records:
        dynamodb_client.put_item(
            TableName="orders",
            Item=record,
        )

    return {"order_id": order_id, "records": records}


@pytest.fixture(scope="function")
def cleanup_orders(dynamodb_client):
    orders_to_cleanup = []
    yield orders_to_cleanup

    response = dynamodb_client.describe_table(TableName="orders")
    print(response["Table"]["KeySchema"])

    # Cleanup logic
    for order in orders_to_cleanup:
        try:
            dynamodb_client.delete_item(
                Key={
                    "order_id": {"S": order.get("order_id")},
                },
                TableName="orders",
            )
            print(f"Deleted test order: {order.get('order_id')}")
        except Exception as e:
            print(f"Failed to delete order {order.get('order_id')}: {e}")
            raise e


@pytest.fixture(scope="function")
def function_dessert(dynamodb_client):
    dessert_id = str(uuid.uuid4())

    records = [
        {
            "dessert_id": {"S": dessert_id},
            "name": {"S": "INT_TEST_DESSERT_NAME"},
            "description": {"S": "INT_TEST_DESCRIPTION"},
            "dessert_type": {"S": "cake"},
            "created_at": {"N": f"{int(datetime.now(tz=timezone.utc).timestamp())}"},
            "last_updated_at": {
                "N": f"{int(datetime.now(tz=timezone.utc).timestamp())}"
            },
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
    ]

    for record in records:
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

    return {"dessert_id": dessert_id, "records": records}


@pytest.fixture(scope="function")
def cleanup_desserts(dynamodb_client):
    desserts_to_cleanup = []
    yield desserts_to_cleanup

    # Cleanup logic
    for dessert in desserts_to_cleanup:
        try:
            dessert_prices = dynamodb_client.query(
                TableName="prices",
                KeyConditionExpression="dessert_id = :dessert_id",
                ExpressionAttributeValues={
                    ":dessert_id": {"S": dessert.get("dessert_id")}
                },
            )
            for price in dessert_prices.get("Items"):
                dynamodb_client.delete_item(
                    Key={
                        "dessert_id": {"S": dessert.get("dessert_id")},
                        "size": price.get("size"),
                    },
                    TableName="prices",
                )
            print(f"Deleted test dessert prices: {dessert.get('dessert_id')}")
            dynamodb_client.delete_item(
                Key={
                    "dessert_id": {"S": dessert.get("dessert_id")},
                },
                TableName="desserts",
            )
            print(f"Deleted test dessert: {dessert.get('dessert_id')}")
        except Exception as e:
            print(f"Failed to delete dessert {dessert.get('dessert_id')}: {e}")
            raise e
