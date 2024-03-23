import pytest
from freezegun import freeze_time
from botocore.stub import Stubber
from fastapi.testclient import TestClient
from src import app
from src.routes.get_orders import orders_table

test_client = TestClient(app)


@pytest.fixture(autouse=True, scope="function")
def orders_dynamodb_stub():
    with Stubber(orders_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


@freeze_time("2024-03-22 12:00:00")
def test_handler_valid_event_get_orders(orders_dynamodb_stub):
    orders_dynamodb_stub.add_response(
        "scan",
        {
            "Items": [
                {
                    "order_id": {"S": "ORDER-1"},
                    "dessert_id": {"S": "DESSERT-1"},
                    "dessert_name": {"S": "Chocolate Cake"},
                    "quantity": {"N": "1"},
                    "customer_first_name": {"S": "Megan"},
                    "customer_last_name": {"S": "Campbell"},
                    "customer_email": {"S": "megan.campbell@gmail.com"},
                    "customer_phone_number": {"S": "555-555-5555"},
                    "customer_zip_code": {"S": "90210"},
                    "delivery_address": {"S": "123 Main St, Los Angeles, CA 90210"},
                    "scheduled_delivery_time": {"N": "1711108800"},
                    "order_total": {"N": "10.00"},
                    "order_status": {"S": "NEW"},
                    "order_date": {"N": "1711108800"},
                },
            ],
        },
        expected_params={"TableName": "orders"},
    )

    response = test_client.get("/v1/orders")

    pytest.helpers.assert_responses_equal(
        response,
        200,
        [
            {
                "order_id": "ORDER-1",
                "dessert_id": "DESSERT-1",
                "dessert_name": "Chocolate Cake",
                "quantity": 1,
                "customer_first_name": "Megan",
                "customer_last_name": "Campbell",
                "customer_email": "megan.campbell@gmail.com",
                "customer_phone_number": "555-555-5555",
                "customer_zip_code": "90210",
                "delivery_address": "123 Main St, Los Angeles, CA 90210",
                "scheduled_delivery_time": 1711108800,
                "order_total": 10.00,
                "order_status": "NEW",
                "order_date": 1711108800,
            }
        ],
    )


@freeze_time("2024-03-22 12:00:00")
def test_handler_valid_event_get_orders_no_orders(orders_dynamodb_stub):
    orders_dynamodb_stub.add_response(
        "scan", {}, expected_params={"TableName": "orders"}
    )

    response = test_client.get("/v1/orders")

    pytest.helpers.assert_responses_equal(response, 404, [])
