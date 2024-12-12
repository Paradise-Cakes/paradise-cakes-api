import logging
from unittest.mock import patch

import pytest
from boto3.dynamodb.conditions import Key
from botocore.stub import Stubber
from fastapi.testclient import TestClient
from freezegun import freeze_time

from src.api import app
from src.routes.get_orders import orders_table

logger = logging.getLogger()
test_client = TestClient(app, headers={"Authorization": "Bearer TOKEN"})


@pytest.fixture(autouse=True, scope="function")
def orders_dynamodb_stub():
    with Stubber(orders_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


@freeze_time("2024-12-12 12:00:00")
def test_handler_valid_event_get_orders_for_order_date(orders_dynamodb_stub):
    orders_dynamodb_stub.add_response(
        "query",
        {
            "Items": [
                {
                    "order_id": {"S": "ORDER-1"},
                    "customer_first_name": {"S": "John"},
                    "customer_last_name": {"S": "Doe"},
                    "customer_full_name": {"S": "John Doe"},
                    "customer_email": {"S": "john.doe@gmail.com"},
                    "customer_phone_number": {"S": "1234567890"},
                    "delivery_zip_code": {"S": "12345"},
                    "delivery_address_line_1": {"S": "123 Main St"},
                    "delivery_address_line_2": {"S": "Apt 1"},
                    "delivery_date": {"S": "12-12-2024"},
                    "delivery_time": {"N": "12"},
                    "order_status": {"S": "NEW"},
                    "order_date": {"S": "12-12-2024"},
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
                    "last_updated_at": {"N": "1734004800"},
                }
            ],
        },
        expected_params={
            "IndexName": "order_date_index",
            "KeyConditionExpression": Key("order_date").eq("12-12-2024"),
            "TableName": "orders",
        },
    )

    response = test_client.get("/v1/orders?order_date=12-12-2024")

    pytest.helpers.assert_responses_equal(
        response,
        200,
        [
            {
                "order_id": "ORDER-1",
                "customer_first_name": "John",
                "customer_last_name": "Doe",
                "customer_full_name": "John Doe",
                "customer_email": "john.doe@gmail.com",
                "customer_phone_number": "1234567890",
                "delivery_zip_code": "12345",
                "delivery_address_line_1": "123 Main St",
                "delivery_address_line_2": "Apt 1",
                "delivery_date": "12-12-2024",
                "delivery_time": 12,
                "order_status": "NEW",
                "order_date": "12-12-2024",
                "order_time": 12,
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
                "last_updated_at": 1734004800,
            }
        ],
    )


@freeze_time("2024-12-12 12:00:00")
def test_handler_valid_event_get_orders_for_delivery_date(orders_dynamodb_stub):
    orders_dynamodb_stub.add_response(
        "query",
        {
            "Items": [
                {
                    "order_id": {"S": "ORDER-1"},
                    "customer_first_name": {"S": "John"},
                    "customer_last_name": {"S": "Doe"},
                    "customer_full_name": {"S": "John Doe"},
                    "customer_email": {"S": "john.doe@gmail.com"},
                    "customer_phone_number": {"S": "1234567890"},
                    "delivery_zip_code": {"S": "12345"},
                    "delivery_address_line_1": {"S": "123 Main St"},
                    "delivery_address_line_2": {"S": "Apt 1"},
                    "delivery_date": {"S": "12-12-2024"},
                    "delivery_time": {"N": "12"},
                    "order_status": {"S": "NEW"},
                    "order_date": {"S": "12-12-2024"},
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
                    "last_updated_at": {"N": "1734004800"},
                }
            ],
        },
        expected_params={
            "IndexName": "delivery_date_index",
            "KeyConditionExpression": Key("delivery_date").eq("12-12-2024"),
            "TableName": "orders",
        },
    )

    response = test_client.get("/v1/orders?delivery_date=12-12-2024")

    pytest.helpers.assert_responses_equal(
        response,
        200,
        [
            {
                "order_id": "ORDER-1",
                "customer_first_name": "John",
                "customer_last_name": "Doe",
                "customer_full_name": "John Doe",
                "customer_email": "john.doe@gmail.com",
                "customer_phone_number": "1234567890",
                "delivery_zip_code": "12345",
                "delivery_address_line_1": "123 Main St",
                "delivery_address_line_2": "Apt 1",
                "delivery_date": "12-12-2024",
                "delivery_time": 12,
                "order_status": "NEW",
                "order_date": "12-12-2024",
                "order_time": 12,
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
                "last_updated_at": 1734004800,
            }
        ],
    )


@freeze_time("2024-12-12 12:00:00")
def test_handler_valid_event_get_orders_for_customer_full_name(orders_dynamodb_stub):
    orders_dynamodb_stub.add_response(
        "query",
        {
            "Items": [
                {
                    "order_id": {"S": "ORDER-1"},
                    "customer_first_name": {"S": "John"},
                    "customer_last_name": {"S": "Doe"},
                    "customer_full_name": {"S": "John Doe"},
                    "customer_email": {"S": "john.doe@gmail.com"},
                    "customer_phone_number": {"S": "1234567890"},
                    "delivery_zip_code": {"S": "12345"},
                    "delivery_address_line_1": {"S": "123 Main St"},
                    "delivery_address_line_2": {"S": "Apt 1"},
                    "delivery_date": {"S": "12-12-2024"},
                    "delivery_time": {"N": "12"},
                    "order_status": {"S": "NEW"},
                    "order_date": {"S": "12-12-2024"},
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
                    "last_updated_at": {"N": "1734004800"},
                }
            ],
        },
        expected_params={
            "IndexName": "customer_full_name_index",
            "KeyConditionExpression": Key("customer_full_name").eq("John Doe"),
            "TableName": "orders",
        },
    )

    response = test_client.get("/v1/orders?customer_full_name=John Doe")

    pytest.helpers.assert_responses_equal(
        response,
        200,
        [
            {
                "order_id": "ORDER-1",
                "customer_first_name": "John",
                "customer_last_name": "Doe",
                "customer_full_name": "John Doe",
                "customer_email": "john.doe@gmail.com",
                "customer_phone_number": "1234567890",
                "delivery_zip_code": "12345",
                "delivery_address_line_1": "123 Main St",
                "delivery_address_line_2": "Apt 1",
                "delivery_date": "12-12-2024",
                "delivery_time": 12,
                "order_status": "NEW",
                "order_date": "12-12-2024",
                "order_time": 12,
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
                "last_updated_at": 1734004800,
            }
        ],
    )


@freeze_time("2024-12-12 12:00:00")
def test_handler_valid_event_get_orders_no_query_params(orders_dynamodb_stub):
    response = test_client.get("/v1/orders")
    pytest.helpers.assert_responses_equal(response, 400, [])


@freeze_time("2024-12-12 12:00:00")
def test_handler_valid_event_get_orders_no_orders(orders_dynamodb_stub):
    orders_dynamodb_stub.add_response(
        "query",
        {},
        expected_params={
            "IndexName": "order_date_index",
            "KeyConditionExpression": Key("order_date").eq("12-12-2024"),
            "TableName": "orders",
        },
    )

    response = test_client.get("/v1/orders?order_date=12-12-2024")

    pytest.helpers.assert_responses_equal(response, 404, [])
    app.dependency_overrides = {}
