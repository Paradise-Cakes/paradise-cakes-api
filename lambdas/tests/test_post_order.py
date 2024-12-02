import pytest
from freezegun import freeze_time
from botocore.stub import Stubber
from decimal import Decimal
from fastapi.testclient import TestClient
from src.api import app
from src.routes.post_order import orders_table, order_type_count_table

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


@freeze_time("2024-03-22 12:00:00")
def test_handler_valid_event_existing_order_type(
    orders_dynamodb_stub, orders_type_count_dynamodb_stub
):
    orders_dynamodb_stub.add_response(
        "query",
        {"Items": [{"order_id": {"S": "ORDER-1"}}]},
        expected_params={
            "IndexName": "scheduled_delivery_time_index",
            "KeyConditionExpression": "scheduled_delivery_time BETWEEN :start AND :end",
            "ExpressionAttributeValues": {":start": 1708041600, ":end": 1708127999},
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

    orders_dynamodb_stub.add_response(
        "put_item",
        {},
        expected_params={
            "Item": {
                "order_id": "ORDER-2",
                "order_status": "NEW",
                "order_date": 1711108800,
                "dessert_id": "1",
                "dessert_name": "chocolate cake",
                "quantity": 2,
                "customer_first_name": "Anthony",
                "customer_last_name": "Viera",
                "customer_email": "anthony.viera@gmail.com",
                "customer_phone_number": "911",
                "delivery_zip_code": "78643",
                "delivery_address_line_1": "my house",
                "delivery_address_line_2": "APT 1",
                "scheduled_delivery_time": 1708084801,
                "order_total": Decimal(3.50),
                "custom_order": False,
            },
            "TableName": "orders",
        },
    )

    response = test_client.post(
        "/orders",
        json={
            "dessert_id": "1",
            "dessert_name": "chocolate cake",
            "quantity": 2,
            "customer_first_name": "Anthony",
            "customer_last_name": "Viera",
            "customer_email": "anthony.viera@gmail.com",
            "customer_phone_number": "911",
            "delivery_zip_code": "78643",
            "delivery_address_line_1": "my house",
            "delivery_address_line_2": "APT 1",
            "scheduled_delivery_time": 1708084801,
            "order_total": 3.50,
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        201,
        {
            "order_id": "ORDER-2",
            "dessert_id": "1",
            "dessert_name": "chocolate cake",
            "quantity": 2,
            "customer_first_name": "Anthony",
            "customer_last_name": "Viera",
            "customer_email": "anthony.viera@gmail.com",
            "customer_phone_number": "911",
            "delivery_zip_code": "78643",
            "delivery_address_line_1": "my house",
            "delivery_address_line_2": "APT 1",
            "scheduled_delivery_time": 1708084801,
            "order_total": 3.5,
            "order_status": "NEW",
            "order_date": 1711108800,
            "custom_order": False,
        },
    )


@freeze_time("2024-03-22 12:00:00")
def test_handler_valid_event_new_order_type(
    orders_dynamodb_stub, orders_type_count_dynamodb_stub
):
    orders_dynamodb_stub.add_response(
        "query",
        {"Items": []},
        expected_params={
            "IndexName": "scheduled_delivery_time_index",
            "KeyConditionExpression": "scheduled_delivery_time BETWEEN :start AND :end",
            "ExpressionAttributeValues": {":start": 1707955200, ":end": 1708041599},
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

    orders_dynamodb_stub.add_response(
        "put_item",
        {},
        expected_params={
            "Item": {
                "order_id": "ORDER-1",
                "order_status": "NEW",
                "order_date": 1711108800,
                "dessert_id": "1",
                "dessert_name": "chocolate cake",
                "quantity": 2,
                "customer_first_name": "Anthony",
                "customer_last_name": "Viera",
                "customer_email": "anthony.viera@gmail.com",
                "customer_phone_number": "911",
                "delivery_zip_code": "78643",
                "delivery_address_line_1": "my house",
                "delivery_address_line_2": "APT 1",
                "scheduled_delivery_time": 1707998401,
                "order_total": Decimal(3.50),
                "custom_order": False,
            },
            "TableName": "orders",
        },
    )

    response = test_client.post(
        "/orders",
        json={
            "dessert_id": "1",
            "dessert_name": "chocolate cake",
            "quantity": 2,
            "customer_first_name": "Anthony",
            "customer_last_name": "Viera",
            "customer_email": "anthony.viera@gmail.com",
            "customer_phone_number": "911",
            "delivery_zip_code": "78643",
            "delivery_address_line_1": "my house",
            "delivery_address_line_2": "APT 1",
            "scheduled_delivery_time": 1707998401,
            "order_total": 3.50,
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        201,
        {
            "order_id": "ORDER-1",
            "dessert_id": "1",
            "dessert_name": "chocolate cake",
            "quantity": 2,
            "customer_first_name": "Anthony",
            "customer_last_name": "Viera",
            "customer_email": "anthony.viera@gmail.com",
            "customer_phone_number": "911",
            "delivery_zip_code": "78643",
            "delivery_address_line_1": "my house",
            "delivery_address_line_2": "APT 1",
            "scheduled_delivery_time": 1707998401,
            "order_total": 3.5,
            "order_status": "NEW",
            "order_date": 1711108800,
            "custom_order": False,
        },
    )


@freeze_time("2024-03-22 12:00:00")
def test_handler_accepts_customer_order(
    orders_dynamodb_stub, orders_type_count_dynamodb_stub
):
    orders_dynamodb_stub.add_response(
        "query",
        {"Items": []},
        expected_params={
            "IndexName": "scheduled_delivery_time_index",
            "KeyConditionExpression": "scheduled_delivery_time BETWEEN :start AND :end",
            "ExpressionAttributeValues": {":start": 1707955200, ":end": 1708041599},
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

    orders_dynamodb_stub.add_response(
        "put_item",
        {},
        expected_params={
            "Item": {
                "order_id": "ORDER-1",
                "order_status": "NEW",
                "order_date": 1711108800,
                "customer_first_name": "Anthony",
                "customer_last_name": "Viera",
                "customer_email": "anthony.viera@gmail.com",
                "customer_phone_number": "911",
                "delivery_zip_code": "78643",
                "delivery_address_line_1": "my house",
                "delivery_address_line_2": "APT 1",
                "scheduled_delivery_time": 1707998401,
                "custom_order": True,
            },
            "TableName": "orders",
        },
    )

    response = test_client.post(
        "/orders",
        json={
            "customer_first_name": "Anthony",
            "customer_last_name": "Viera",
            "customer_email": "anthony.viera@gmail.com",
            "customer_phone_number": "911",
            "delivery_zip_code": "78643",
            "delivery_address_line_1": "my house",
            "delivery_address_line_2": "APT 1",
            "scheduled_delivery_time": 1707998401,
            "custom_order": True,
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        201,
        {
            "order_id": "ORDER-1",
            "customer_first_name": "Anthony",
            "customer_last_name": "Viera",
            "customer_email": "anthony.viera@gmail.com",
            "customer_phone_number": "911",
            "delivery_zip_code": "78643",
            "delivery_address_line_1": "my house",
            "delivery_address_line_2": "APT 1",
            "scheduled_delivery_time": 1707998401,
            "order_status": "NEW",
            "order_date": 1711108800,
            "custom_order": True,
        },
    )


@freeze_time("2024-03-22 12:00:00")
def test_handler_rejects_order_when_max_orders_exceeded(
    orders_dynamodb_stub, orders_type_count_dynamodb_stub
):
    orders_dynamodb_stub.add_response(
        "query",
        {"Items": [{"order_id": {"S": "ORDER-1"}}, {"order_id": {"S": "ORDER-2"}}]},
        expected_params={
            "IndexName": "scheduled_delivery_time_index",
            "KeyConditionExpression": "scheduled_delivery_time BETWEEN :start AND :end",
            "ExpressionAttributeValues": {":start": 1707955200, ":end": 1708041599},
            "TableName": "orders",
        },
    )

    orders_type_count_dynamodb_stub.add_response(
        "get_item",
        {"Item": {"order_type": {"S": "ORDER"}, "order_count": {"S": "2"}}},
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

    response = test_client.post(
        "/orders",
        json={
            "customer_first_name": "Anthony",
            "customer_last_name": "Viera",
            "customer_email": "anthony.viera@gmail.com",
            "customer_phone_number": "911",
            "delivery_zip_code": "78643",
            "delivery_address_line_1": "my house",
            "delivery_address_line_2": "APT 1",
            "scheduled_delivery_time": 1707998401,
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {"error": "Order limit of 2 exceeded for date: 2024-02-15"},
    )


@freeze_time("2024-03-22 12:00:00")
def test_handler_rejects_order_when_max_orders_exceeded(orders_dynamodb_stub):
    orders_dynamodb_stub.add_response(
        "query",
        {"Items": [{"order_id": {"S": "ORDER-1"}}, {"order_id": {"S": "ORDER-2"}}]},
        expected_params={
            "IndexName": "scheduled_delivery_time_index",
            "KeyConditionExpression": "scheduled_delivery_time BETWEEN :start AND :end",
            "ExpressionAttributeValues": {":start": 1707955200, ":end": 1708041599},
            "TableName": "orders",
        },
    )

    response = test_client.post(
        "/orders",
        json={
            "customer_first_name": "Anthony",
            "customer_last_name": "Viera",
            "customer_email": "anthony.viera@gmail.com",
            "customer_phone_number": "911",
            "delivery_zip_code": "78643",
            "delivery_address_line_1": "my house",
            "delivery_address_line_2": "APT 1",
            "scheduled_delivery_time": 1707998401,
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {"error": "Order limit exceeded for 2024-02-15. Max orders: 2"},
    )
