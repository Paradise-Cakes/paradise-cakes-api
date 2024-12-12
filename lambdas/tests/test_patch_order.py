from decimal import Decimal

import pytest
from botocore.stub import Stubber
from fastapi.testclient import TestClient
from freezegun import freeze_time

from src.api import app
from src.routes.patch_order import orders_table

test_client = TestClient(app)


@pytest.fixture(autouse=True, scope="function")
def orders_dynamodb_stub():
    with Stubber(orders_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


@freeze_time("2024-12-12 12:00:00")
def test_handler_valid_event_patch_order(orders_dynamodb_stub):
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
                "last_updated_at": {"N": "123456789"},
            }
        },
    )

    orders_dynamodb_stub.add_response(
        "update_item",
        {
            "Attributes": {
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
                "order_status": {"S": "PENDING"},
                "order_date": {"S": "11-11-2024"},
                "order_time": {"N": "123456789"},
                "approved": {"BOOL": True},
                "custom_order": {"BOOL": False},
                "order_total": {"N": "20.00"},
                "last_updated_at": {"N": "1734026222"},
            }
        },
        expected_params={
            "TableName": "orders",
            "Key": {"order_id": "ORDER-1"},
            "UpdateExpression": "SET #order_status = :order_status, #approved = :approved, #order_total = :order_total, #last_updated_at = :last_updated_at",
            "ExpressionAttributeValues": {
                ":approved": True,
                ":order_status": "PENDING",
                ":last_updated_at": 1734004800,
                ":order_total": Decimal(20),
            },
            "ExpressionAttributeNames": {
                "#approved": "approved",
                "#last_updated_at": "last_updated_at",
                "#order_total": "order_total",
                "#order_status": "order_status",
            },
            "ReturnValues": "ALL_NEW",
        },
    )

    response = test_client.patch(
        "/orders/ORDER-1",
        json={
            "approved": True,
            "order_total": 20.00,
            "order_status": "PENDING",
        },
    )

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
            "order_status": "PENDING",
            "order_date": "11-11-2024",
            "order_time": 123456789,
            "approved": True,
            "custom_order": False,
            "order_total": 20.00,
            "last_updated_at": 1734026222,
            "desserts": [],
        },
    )


@freeze_time("2024-12-12 12:00:00")
def test_handler_patch_order_not_found(orders_dynamodb_stub):
    orders_dynamodb_stub.add_response(
        "get_item",
        {},
        expected_params={"TableName": "orders", "Key": {"order_id": "ORDER-1"}},
    )

    response = test_client.patch(
        "/orders/ORDER-1",
        json={
            "approved": True,
            "order_total": 20.00,
            "order_status": "PENDING",
        },
    )

    pytest.helpers.assert_responses_equal(response, 404, {"detail": "Order not found"})
