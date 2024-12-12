import pytest
from botocore.stub import Stubber
from fastapi.testclient import TestClient
from freezegun import freeze_time

from src.api import app
from src.routes.get_order import orders_table

test_client = TestClient(app)


@pytest.fixture(autouse=True, scope="function")
def orders_dynamodb_stub():
    with Stubber(orders_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


@freeze_time("2024-12-12 12:00:00")
def test_handler_valid_event_get_order(orders_dynamodb_stub):
    orders_dynamodb_stub.add_response(
        "get_item",
        {
            "Item": {
                "order_id": {"S": "ORDER-1"},
                "customer_first_name": {"S": "Anthony"},
                "customer_last_name": {"S": "Soprano"},
                "customer_full_name": {"S": "Anthony Soprano"},
                "customer_email": {"S": "anthony.soprano@gmail.com"},
                "customer_phone_number": {"S": "123456789"},
                "delivery_zip_code": {"S": "76177"},
                "delivery_address_line_1": {"S": "123 Elm St"},
                "delivery_address_line_2": {"S": "APT 1"},
                "delivery_date": {"S": "12-12-2024"},
                "delivery_time": {"N": "123456789"},
                "order_status": {"S": "NEW"},
                "order_date": {"S": "11-11-2024"},
                "order_time": {"N": "123456789"},
                "approved": {"BOOL": False},
                "custom_order": {"BOOL": False},
                "order_total": {"N": "0.00"},
                "desserts": {
                    "L": [
                        {
                            "M": {
                                "dessert_id": {"S": "DESSERT-1"},
                                "dessert_name": {"S": "Chocolate Cake"},
                                "size": {"S": "6 inch"},
                                "quantity": {"N": "2"},
                            }
                        },
                        {
                            "M": {
                                "dessert_id": {"S": "DESSERT-2"},
                                "dessert_name": {"S": "Vanilla Cake"},
                                "size": {"S": "6 inch"},
                                "quantity": {"N": "1"},
                            }
                        },
                    ]
                },
                "last_updated_at": {"N": "123456789"},
            }
        },
        expected_params={"TableName": "orders", "Key": {"order_id": "ORDER-1"}},
    )

    response = test_client.get("/orders/ORDER-1")

    pytest.helpers.assert_responses_equal(
        response,
        200,
        {
            "order_id": "ORDER-1",
            "customer_first_name": "Anthony",
            "customer_last_name": "Soprano",
            "customer_full_name": "Anthony Soprano",
            "customer_email": "anthony.soprano@gmail.com",
            "customer_phone_number": "123456789",
            "delivery_zip_code": "76177",
            "delivery_address_line_1": "123 Elm St",
            "delivery_address_line_2": "APT 1",
            "delivery_date": "12-12-2024",
            "delivery_time": 123456789,
            "order_status": "NEW",
            "order_date": "11-11-2024",
            "order_time": 123456789,
            "approved": False,
            "custom_order": False,
            "order_total": 0.00,
            "desserts": [
                {
                    "dessert_id": "DESSERT-1",
                    "dessert_name": "Chocolate Cake",
                    "size": "6 inch",
                    "quantity": 2,
                },
                {
                    "dessert_id": "DESSERT-2",
                    "dessert_name": "Vanilla Cake",
                    "size": "6 inch",
                    "quantity": 1,
                },
            ],
            "last_updated_at": 123456789,
        },
    )


def test_handler_valid_event_get_order_not_found(orders_dynamodb_stub):
    orders_dynamodb_stub.add_response(
        "get_item",
        {},
        expected_params={"TableName": "orders", "Key": {"order_id": "ORDER-1"}},
    )

    response = test_client.get("/orders/ORDER-1")

    pytest.helpers.assert_responses_equal(response, 404, {"detail": "Order not found"})
