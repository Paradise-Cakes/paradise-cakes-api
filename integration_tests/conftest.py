import pytest
import boto3
import uuid

from datetime import datetime, timezone
from request_helper import RequestHelper


@pytest.fixture(scope="session")
def api_url():
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
                    "order_id": {"S": order["order_id"]},
                },
                TableName="orders",
            )
            print(f"Deleted test order: {order["order_id"]}")
        except Exception as e:
            print(f"Failed to delete order {order["order_id"]}: {e}")
            raise e
