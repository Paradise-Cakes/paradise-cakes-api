import pytest
from boto3.dynamodb.conditions import Key
from botocore.stub import Stubber
from fastapi.testclient import TestClient
from freezegun import freeze_time

from src.api import app
from src.routes.get_dessert import desserts_table, prices_table

test_client = TestClient(app)


@pytest.fixture(autouse=True, scope="function")
def desserts_dynamodb_stub():
    with Stubber(desserts_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


@pytest.fixture(autouse=True, scope="function")
def prices_dynamodb_stub():
    with Stubber(prices_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


@freeze_time("2024-03-22 12:00:00")
def test_handler_valid_event_get_dessert(desserts_dynamodb_stub, prices_dynamodb_stub):
    desserts_dynamodb_stub.add_response(
        "get_item",
        {
            "Item": {
                "dessert_id": {"S": "DESSERT-1"},
                "name": {"S": "Chocolate Cake"},
                "description": {"S": "A delicious chocolate cake"},
                "dessert_type": {"S": "cake"},
                "created_at": {"N": "1711108800"},
                "last_updated_at": {"N": "1711108800"},
                "visible": {"BOOL": False},
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
                                "position": {"N": "1"},
                                "file_type": {"S": "jpg"},
                            }
                        },
                        {
                            "M": {
                                "image_id": {"S": "IMAGE-2"},
                                "url": {"S": "https://example.com/image2.jpg"},
                                "position": {"N": "2"},
                                "file_type": {"S": "jpg"},
                            }
                        },
                    ]
                },
            }
        },
        expected_params={
            "TableName": "desserts",
            "Key": {"dessert_id": "DESSERT-1"},
        },
    )

    prices_dynamodb_stub.add_response(
        "query",
        {
            "Items": [
                {
                    "dessert_id": {"S": "DESSERT-1"},
                    "size": {"S": "6in"},
                    "base_price": {"N": "10.00"},
                    "discount": {"N": "0.00"},
                },
                {
                    "dessert_id": {"S": "DESSERT-1"},
                    "size": {"S": "8in"},
                    "base_price": {"N": "15.00"},
                    "discount": {"N": "0.00"},
                },
                {
                    "dessert_id": {"S": "DESSERT-1"},
                    "size": {"S": "10in"},
                    "base_price": {"N": "20.00"},
                    "discount": {"N": "0.00"},
                },
            ]
        },
        expected_params={
            "TableName": "prices",
            "KeyConditionExpression": Key("dessert_id").eq("DESSERT-1"),
        },
    )

    response = test_client.get("/v1/desserts/DESSERT-1")

    pytest.helpers.assert_responses_equal(
        response,
        200,
        {
            "dessert_id": "DESSERT-1",
            "name": "Chocolate Cake",
            "description": "A delicious chocolate cake",
            "dessert_type": "cake",
            "created_at": 1711108800,
            "last_updated_at": 1711108800,
            "visible": False,
            "prices": [
                {
                    "dessert_id": "DESSERT-1",
                    "size": "6in",
                    "base_price": 10.00,
                    "discount": 0.00,
                },
                {
                    "dessert_id": "DESSERT-1",
                    "size": "8in",
                    "base_price": 15.00,
                    "discount": 0.00,
                },
                {
                    "dessert_id": "DESSERT-1",
                    "size": "10in",
                    "base_price": 20.00,
                    "discount": 0.00,
                },
            ],
            "ingredients": ["flour", "sugar", "cocoa", "butter", "eggs"],
            "images": [
                {
                    "image_id": "IMAGE-1",
                    "url": "https://example.com/image1.jpg",
                    "position": 1,
                    "file_type": "jpg",
                },
                {
                    "image_id": "IMAGE-2",
                    "url": "https://example.com/image2.jpg",
                    "position": 2,
                    "file_type": "jpg",
                },
            ],
        },
    )


@freeze_time("2024-03-22 12:00:00")
def test_handler_valid_event_get_dessert_not_found(desserts_dynamodb_stub):
    desserts_dynamodb_stub.add_response(
        "get_item",
        {},
        expected_params={
            "TableName": "desserts",
            "Key": {"dessert_id": "DESSERT-1"},
        },
    )

    response = test_client.get("/v1/desserts/DESSERT-1")

    pytest.helpers.assert_responses_equal(
        response, 404, {"detail": "Dessert not found"}
    )
