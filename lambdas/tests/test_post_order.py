from decimal import Decimal

import pytest
from botocore.stub import Stubber
from fastapi.testclient import TestClient
from freezegun import freeze_time

from src.api import app
from src.routes.post_order import order_type_count_table, orders_table, prices_table

test_client = TestClient(app)


@pytest.fixture(autouse=True, scope="function")
def orders_dynamodb_stub():
    with Stubber(orders_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


@pytest.fixture(autouse=True, scope="function")
def orders_type_count_dynamodb_stub():
    with Stubber(order_type_count_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


@pytest.fixture(autouse=True, scope="function")
def prices_dynamodb_stub():
    with Stubber(prices_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


@freeze_time("2024-12-12 12:00:00")
def test_handler_valid_event_existing_order_type(
    orders_dynamodb_stub, orders_type_count_dynamodb_stub, prices_dynamodb_stub
):
    orders_dynamodb_stub.add_response(
        "query",
        {"Items": [{"order_id": {"S": "ORDER-1"}}]},
        expected_params={
            "IndexName": "delivery_date_index",
            "KeyConditionExpression": "delivery_date = :date",
            "ExpressionAttributeValues": {":date": "12-12-2024"},
            "TableName": "orders",
        },
    )

    orders_type_count_dynamodb_stub.add_response(
        "get_item",
        {"Item": {"order_type": {"S": "ORDER"}, "order_count": {"S": "1"}}},
        expected_params={
            "Key": {"order_type": "ORDER"},
            "TableName": "order_type_count",
        },
    )

    orders_type_count_dynamodb_stub.add_response(
        "update_item",
        {"Attributes": {"order_count": {"S": "2"}}},
        expected_params={
            "Key": {"order_type": "ORDER"},
            "TableName": "order_type_count",
            "UpdateExpression": "set order_count = order_count + :incr",
            "ExpressionAttributeValues": {":incr": 1},
            "ReturnValues": "ALL_NEW",
        },
    )

    prices_dynamodb_stub.add_response(
        "get_item",
        {
            "Item": {
                "dessert_id": {"S": "UNIT_TEST-6aa579b6-524d-4d1e-b534-a480b0f1110"},
                "size": {"S": "6 inch"},
                "base_price": {"N": "25.30"},
                "discount": {"N": "0.35"},
            }
        },
        expected_params={
            "Key": {
                "dessert_id": "UNIT_TEST-6aa579b6-524d-4d1e-b534-a480b0f1110",
                "size": "6 inch",
            },
            "TableName": "prices",
        },
    )

    orders_dynamodb_stub.add_response(
        "put_item",
        {},
        expected_params={
            "Item": {
                "order_id": "ORDER-2",
                "customer_first_name": "Anthony",
                "customer_last_name": "Soprano",
                "customer_full_name": "Anthony Soprano",
                "customer_email": "anthony.soprano@gmail.com",
                "customer_phone_number": "555-555-5555",
                "delivery_zip_code": "07001",
                "delivery_address_line_1": "123 Main St",
                "delivery_address_line_2": "Apt 1",
                "delivery_date": "12-12-2024",
                "delivery_time": 1734004800,
                "order_status": "NEW",
                "order_date": "12-12-2024",
                "order_time": 1734004800,
                "approved": False,
                "custom_order": False,
                "order_total": Decimal("49.90"),
                "desserts": [
                    {
                        "dessert_id": "UNIT_TEST-6aa579b6-524d-4d1e-b534-a480b0f1110",
                        "dessert_name": "Lemon Blueberry Cake",
                        "size": "6 inch",
                        "quantity": 2,
                    }
                ],
                "last_updated_at": 1734004800,
            },
            "TableName": "orders",
        },
    )

    response = test_client.post(
        "/orders",
        json={
            "desserts": [
                {
                    "dessert_id": "UNIT_TEST-6aa579b6-524d-4d1e-b534-a480b0f1110",
                    "dessert_name": "Lemon Blueberry Cake",
                    "size": "6 inch",
                    "quantity": 2,
                }
            ],
            "customer_first_name": "Anthony",
            "customer_last_name": "Soprano",
            "customer_email": "anthony.soprano@gmail.com",
            "customer_phone_number": "555-555-5555",
            "delivery_zip_code": "07001",
            "delivery_address_line_1": "123 Main St",
            "delivery_address_line_2": "Apt 1",
            "delivery_date": "12-12-2024",
            "delivery_time": 1734004800,
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        201,
        {
            "order_id": "ORDER-2",
            "customer_first_name": "Anthony",
            "customer_last_name": "Soprano",
            "customer_full_name": "Anthony Soprano",
            "customer_email": "anthony.soprano@gmail.com",
            "customer_phone_number": "555-555-5555",
            "delivery_zip_code": "07001",
            "delivery_address_line_1": "123 Main St",
            "delivery_address_line_2": "Apt 1",
            "delivery_date": "12-12-2024",
            "delivery_time": 1734004800,
            "order_status": "NEW",
            "order_date": "12-12-2024",
            "order_time": 1734004800,
            "approved": False,
            "custom_order": False,
            "order_total": 49.90,
            "desserts": [
                {
                    "dessert_id": "UNIT_TEST-6aa579b6-524d-4d1e-b534-a480b0f1110",
                    "dessert_name": "Lemon Blueberry Cake",
                    "size": "6 inch",
                    "quantity": 2,
                }
            ],
            "last_updated_at": 1734004800,
        },
    )


@freeze_time("2024-12-12 12:00:00")
def test_handler_valid_event_new_order_type(
    orders_dynamodb_stub, orders_type_count_dynamodb_stub, prices_dynamodb_stub
):
    orders_dynamodb_stub.add_response(
        "query",
        {"Items": []},
        expected_params={
            "IndexName": "delivery_date_index",
            "KeyConditionExpression": "delivery_date = :date",
            "ExpressionAttributeValues": {":date": "12-12-2024"},
            "TableName": "orders",
        },
    )

    orders_type_count_dynamodb_stub.add_response(
        "get_item",
        {},
        expected_params={
            "Key": {"order_type": "ORDER"},
            "TableName": "order_type_count",
        },
    )

    orders_type_count_dynamodb_stub.add_response(
        "put_item",
        {},
        expected_params={
            "Item": {"order_type": "ORDER", "order_count": 1},
            "TableName": "order_type_count",
        },
    )

    prices_dynamodb_stub.add_response(
        "get_item",
        {
            "Item": {
                "dessert_id": {"S": "UNIT_TEST-6aa579b6-524d-4d1e-b534-a480b0f1110"},
                "size": {"S": "6 inch"},
                "base_price": {"N": "25.30"},
                "discount": {"N": "0.35"},
            }
        },
        expected_params={
            "Key": {
                "dessert_id": "UNIT_TEST-6aa579b6-524d-4d1e-b534-a480b0f1110",
                "size": "6 inch",
            },
            "TableName": "prices",
        },
    )

    orders_dynamodb_stub.add_response(
        "put_item",
        {},
        expected_params={
            "Item": {
                "order_id": "ORDER-1",
                "customer_first_name": "Anthony",
                "customer_last_name": "Viera",
                "customer_full_name": "Anthony Viera",
                "customer_email": "anthony.soprano@gmail.com",
                "customer_phone_number": "555-555-5555",
                "delivery_zip_code": "07001",
                "delivery_address_line_1": "123 Main St",
                "delivery_address_line_2": "Apt 1",
                "delivery_date": "12-12-2024",
                "delivery_time": 1734004800,
                "order_status": "NEW",
                "order_date": "12-12-2024",
                "order_time": 1734004800,
                "approved": False,
                "custom_order": False,
                "order_total": Decimal("49.90"),
                "desserts": [
                    {
                        "dessert_id": "UNIT_TEST-6aa579b6-524d-4d1e-b534-a480b0f1110",
                        "dessert_name": "Lemon Blueberry Cake",
                        "size": "6 inch",
                        "quantity": 2,
                    }
                ],
                "last_updated_at": 1734004800,
            },
            "TableName": "orders",
        },
    )

    response = test_client.post(
        "/orders",
        json={
            "desserts": [
                {
                    "dessert_id": "UNIT_TEST-6aa579b6-524d-4d1e-b534-a480b0f1110",
                    "dessert_name": "Lemon Blueberry Cake",
                    "size": "6 inch",
                    "quantity": 2,
                }
            ],
            "customer_first_name": "Anthony",
            "customer_last_name": "Viera",
            "customer_email": "anthony.soprano@gmail.com",
            "customer_phone_number": "555-555-5555",
            "delivery_zip_code": "07001",
            "delivery_address_line_1": "123 Main St",
            "delivery_address_line_2": "Apt 1",
            "delivery_date": "12-12-2024",
            "delivery_time": 1734004800,
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        201,
        {
            "order_id": "ORDER-1",
            "customer_first_name": "Anthony",
            "customer_last_name": "Viera",
            "customer_full_name": "Anthony Viera",
            "customer_email": "anthony.soprano@gmail.com",
            "customer_phone_number": "555-555-5555",
            "delivery_zip_code": "07001",
            "delivery_address_line_1": "123 Main St",
            "delivery_address_line_2": "Apt 1",
            "delivery_date": "12-12-2024",
            "delivery_time": 1734004800,
            "order_status": "NEW",
            "order_date": "12-12-2024",
            "order_time": 1734004800,
            "approved": False,
            "custom_order": False,
            "order_total": 49.90,
            "desserts": [
                {
                    "dessert_id": "UNIT_TEST-6aa579b6-524d-4d1e-b534-a480b0f1110",
                    "dessert_name": "Lemon Blueberry Cake",
                    "size": "6 inch",
                    "quantity": 2,
                }
            ],
            "last_updated_at": 1734004800,
        },
    )


@freeze_time("2024-12-12 12:00:00")
def test_handler_accepts_customer_order(
    orders_dynamodb_stub, orders_type_count_dynamodb_stub, prices_dynamodb_stub
):
    orders_dynamodb_stub.add_response(
        "query",
        {"Items": []},
        expected_params={
            "IndexName": "delivery_date_index",
            "KeyConditionExpression": "delivery_date = :date",
            "ExpressionAttributeValues": {":date": "12-12-2024"},
            "TableName": "orders",
        },
    )

    orders_type_count_dynamodb_stub.add_response(
        "get_item",
        {},
        expected_params={
            "Key": {"order_type": "ORDER"},
            "TableName": "order_type_count",
        },
    )

    orders_type_count_dynamodb_stub.add_response(
        "put_item",
        {},
        expected_params={
            "Item": {"order_type": "ORDER", "order_count": 1},
            "TableName": "order_type_count",
        },
    )

    prices_dynamodb_stub.add_response(
        "get_item",
        {},
        expected_params={
            "Key": {
                "dessert_id": "UNIT_TEST-6aa579b6-524d-4d1e-b534-a480b0f1110",
                "size": "6 inch",
            },
            "TableName": "prices",
        },
    )

    orders_dynamodb_stub.add_response(
        "put_item",
        {},
        expected_params={
            "Item": {
                "order_id": "ORDER-1",
                "description": "Custom order",
                "customer_first_name": "Anthony",
                "customer_last_name": "Viera",
                "customer_full_name": "Anthony Viera",
                "customer_email": "anthony.soprano@gmail.com",
                "customer_phone_number": "555-555-5555",
                "delivery_zip_code": "07001",
                "delivery_address_line_1": "123 Main St",
                "delivery_address_line_2": "Apt 1",
                "delivery_date": "12-12-2024",
                "delivery_time": 1734004800,
                "order_status": "NEW",
                "order_date": "12-12-2024",
                "order_time": 1734004800,
                "approved": False,
                "custom_order": True,
                "order_total": Decimal("0"),
                "desserts": [
                    {
                        "dessert_id": "UNIT_TEST-6aa579b6-524d-4d1e-b534-a480b0f1110",
                        "dessert_name": "Lemon Blueberry Cake",
                        "size": "6 inch",
                        "quantity": 2,
                    }
                ],
                "last_updated_at": 1734004800,
            },
            "TableName": "orders",
        },
    )

    response = test_client.post(
        "/orders",
        json={
            "desserts": [
                {
                    "dessert_id": "UNIT_TEST-6aa579b6-524d-4d1e-b534-a480b0f1110",
                    "dessert_name": "Lemon Blueberry Cake",
                    "size": "6 inch",
                    "quantity": 2,
                }
            ],
            "description": "Custom order",
            "custom_order": True,
            "customer_first_name": "Anthony",
            "customer_last_name": "Viera",
            "customer_email": "anthony.soprano@gmail.com",
            "customer_phone_number": "555-555-5555",
            "delivery_zip_code": "07001",
            "delivery_address_line_1": "123 Main St",
            "delivery_address_line_2": "Apt 1",
            "delivery_date": "12-12-2024",
            "delivery_time": 1734004800,
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        201,
        {
            "order_id": "ORDER-1",
            "customer_first_name": "Anthony",
            "customer_last_name": "Viera",
            "customer_full_name": "Anthony Viera",
            "customer_email": "anthony.soprano@gmail.com",
            "customer_phone_number": "555-555-5555",
            "delivery_zip_code": "07001",
            "delivery_address_line_1": "123 Main St",
            "delivery_address_line_2": "Apt 1",
            "delivery_date": "12-12-2024",
            "delivery_time": 1734004800,
            "order_status": "NEW",
            "order_date": "12-12-2024",
            "order_time": 1734004800,
            "approved": False,
            "custom_order": True,
            "order_total": 0,
            "description": "Custom order",
            "desserts": [
                {
                    "dessert_id": "UNIT_TEST-6aa579b6-524d-4d1e-b534-a480b0f1110",
                    "dessert_name": "Lemon Blueberry Cake",
                    "size": "6 inch",
                    "quantity": 2,
                }
            ],
            "last_updated_at": 1734004800,
        },
    )


@freeze_time("2024-12-12 12:00:00")
def test_handler_rejects_order_when_max_orders_exceeded(orders_dynamodb_stub):
    orders_dynamodb_stub.add_response(
        "query",
        {"Items": [{"order_id": {"S": "ORDER-1"}}, {"order_id": {"S": "ORDER-2"}}]},
        expected_params={
            "IndexName": "delivery_date_index",
            "KeyConditionExpression": "delivery_date = :date",
            "ExpressionAttributeValues": {":date": "12-12-2024"},
            "TableName": "orders",
        },
    )

    response = test_client.post(
        "/orders",
        json={
            "desserts": [
                {
                    "dessert_id": "UNIT_TEST-6aa579b6-524d-4d1e-b534-a480b0f1110",
                    "dessert_name": "Lemon Blueberry Cake",
                    "size": "6 inch",
                    "quantity": 2,
                }
            ],
            "customer_first_name": "Anthony",
            "customer_last_name": "Viera",
            "customer_email": "anthony.soprano@gmail.com",
            "customer_phone_number": "555-555-5555",
            "delivery_zip_code": "07001",
            "delivery_address_line_1": "123 Main St",
            "delivery_address_line_2": "Apt 1",
            "delivery_date": "12-12-2024",
            "delivery_time": 1734004800,
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {"error": "Order limit exceeded for date: 12-12-2024. Max orders: 2"},
    )


@freeze_time("2024-12-12 12:00:00")
def test_handler_rejects_order_when_dessert_quanitity_exceeded(orders_dynamodb_stub):
    orders_dynamodb_stub.add_response(
        "query",
        {"Items": []},
        expected_params={
            "IndexName": "delivery_date_index",
            "KeyConditionExpression": "delivery_date = :date",
            "ExpressionAttributeValues": {":date": "12-12-2024"},
            "TableName": "orders",
        },
    )

    response = test_client.post(
        "/orders",
        json={
            "desserts": [
                {
                    "dessert_id": "UNIT_TEST-6aa579b6-524d-4d1e-b534-a480b0f1110",
                    "dessert_name": "Lemon Blueberry Cake",
                    "size": "6 inch",
                    "quantity": 3,
                }
            ],
            "customer_first_name": "Anthony",
            "customer_last_name": "Viera",
            "customer_email": "anthony.soprano@gmail.com",
            "customer_phone_number": "555-555-5555",
            "delivery_zip_code": "07001",
            "delivery_address_line_1": "123 Main St",
            "delivery_address_line_2": "Apt 1",
            "delivery_date": "12-12-2024",
            "delivery_time": 1734004800,
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {
            "error": "Dessert quantity limit exceeded for dessert: UNIT_TEST-6aa579b6-524d-4d1e-b534-a480b0f1110. Max quantity: 2"
        },
    )
