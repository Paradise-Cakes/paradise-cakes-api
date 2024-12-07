from decimal import Decimal

import pytest
from botocore.stub import Stubber
from fastapi.testclient import TestClient

from src.api import app
from src.routes.delete_dessert import desserts_table, prices_table, s3_client

test_client = TestClient(app)


@pytest.fixture(autouse=True)
def monkeypatch_env(monkeypatch):
    monkeypatch.setenv("DYNAMODB_REGION", "us-east-1")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_URL", None)
    monkeypatch.setenv("DYNAMODB_DESSERTS_TABLE_NAME", "desserts")
    monkeypatch.setenv("DESSERT_IMAGES_BUCKET_NAME", "dessert-images")
    monkeypatch.setenv("REGION", "us-east-1")


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


@pytest.fixture(autouse=True, scope="function")
def s3_stub():
    with Stubber(s3_client) as s3_stubber:
        yield s3_stubber
        s3_stubber.assert_no_pending_responses()


def test_handler_delete_dessert(desserts_dynamodb_stub, prices_dynamodb_stub, s3_stub):
    desserts_dynamodb_stub.add_response(
        "get_item",
        {
            "Item": {
                "dessert_id": {"S": "00000000-0000-0000-0000-000000000001"},
                "name": {"S": "Chocolate Cake"},
                "description": {"S": "A delicious chocolate cake"},
                "dessert_type": {"S": "cake"},
                "created_at": {"N": "1711108800"},
                "last_updated_at": {"N": "1711108800"},
                "visible": {"BOOL": False},
                "prices": {
                    "L": [
                        {
                            "M": {
                                "dessert_id": {
                                    "S": "00000000-0000-0000-0000-000000000001"
                                },
                                "size": {"S": "6in"},
                                "base_price": {"N": "10.00"},
                                "discount": {"N": "0.00"},
                            }
                        },
                        {
                            "M": {
                                "dessert_id": {
                                    "S": "00000000-0000-0000-0000-000000000001"
                                },
                                "size": {"S": "8in"},
                                "base_price": {"N": "15.00"},
                                "discount": {"N": "0.00"},
                            }
                        },
                        {
                            "M": {
                                "dessert_id": {
                                    "S": "00000000-0000-0000-0000-000000000001"
                                },
                                "size": {"S": "10in"},
                                "base_price": {"N": "20.00"},
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
                                "image_id": {
                                    "S": "00000000-0000-0000-0000-000000000002"
                                },
                                "position": {"N": "1"},
                                "url": {
                                    "S": "https://dessert-images.s3.amazonaws.com/00000000-0000-0000-0000-000000000001/00000000-0000-0000-0000-000000000002"
                                },
                                "file_type": {"S": "image/jpeg"},
                            }
                        }
                    ]
                },
            }
        },
        expected_params={
            "TableName": "desserts",
            "Key": {"dessert_id": "00000000-0000-0000-0000-000000000001"},
        },
    )

    for size in ["6in", "8in", "10in"]:
        prices_dynamodb_stub.add_response(
            "delete_item",
            {},
            expected_params={
                "Key": {
                    "dessert_id": "00000000-0000-0000-0000-000000000001",
                    "size": size,
                },
                "TableName": "prices",
            },
        )

    for image in [
        "00000000-0000-0000-0000-000000000002",
    ]:
        s3_stub.add_response(
            "delete_object",
            {},
            expected_params={
                "Bucket": "dessert-images",
                "Key": f"00000000-0000-0000-0000-000000000001/{image}",
            },
        )

    desserts_dynamodb_stub.add_response(
        "delete_item",
        {},
        expected_params={
            "Key": {"dessert_id": "00000000-0000-0000-0000-000000000001"},
            "TableName": "desserts",
        },
    )

    response = test_client.delete("/desserts/00000000-0000-0000-0000-000000000001")

    pytest.helpers.assert_responses_equal(
        response,
        200,
        {
            "dessert_id": "00000000-0000-0000-0000-000000000001",
            "name": "Chocolate Cake",
            "description": "A delicious chocolate cake",
            "dessert_type": "cake",
            "created_at": 1711108800,
            "last_updated_at": 1711108800,
            "visible": False,
            "prices": [
                {
                    "dessert_id": "00000000-0000-0000-0000-000000000001",
                    "size": "6in",
                    "base_price": 10.00,
                    "discount": 0.00,
                },
                {
                    "dessert_id": "00000000-0000-0000-0000-000000000001",
                    "size": "8in",
                    "base_price": 15.00,
                    "discount": 0.00,
                },
                {
                    "dessert_id": "00000000-0000-0000-0000-000000000001",
                    "size": "10in",
                    "base_price": 20.00,
                    "discount": 0.00,
                },
            ],
            "ingredients": ["flour", "sugar", "cocoa", "butter", "eggs"],
            "images": [
                {
                    "image_id": "00000000-0000-0000-0000-000000000002",
                    "position": 1,
                    "url": "https://dessert-images.s3.amazonaws.com/00000000-0000-0000-0000-000000000001/00000000-0000-0000-0000-000000000002",
                    "file_type": "image/jpeg",
                },
            ],
        },
    )


def test_handler_delete_dessert_not_found(desserts_dynamodb_stub):
    desserts_dynamodb_stub.add_response(
        "get_item",
        {},
        expected_params={
            "TableName": "desserts",
            "Key": {"dessert_id": "00000000-0000-0000-0000-000000000001"},
        },
    )

    response = test_client.delete("/desserts/00000000-0000-0000-0000-000000000001")

    pytest.helpers.assert_responses_equal(
        response,
        404,
        {"detail": "Dessert not found"},
    )
