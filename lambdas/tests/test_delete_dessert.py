import pytest
from botocore.stub import Stubber
from decimal import Decimal
from fastapi.testclient import TestClient
from src.api import app
from src.routes.delete_dessert import desserts_table, s3_client

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
def s3_stub():
    with Stubber(s3_client) as s3_stubber:
        yield s3_stubber
        s3_stubber.assert_no_pending_responses()


def test_handler_delete_dessert(desserts_dynamodb_stub, s3_stub):
    desserts_dynamodb_stub.add_response(
        "get_item",
        {
            "Item": {
                "dessert_id": {"S": "00000000-0000-0000-0000-000000000001"},
                "name": {"S": "Chocolate Cake"},
                "description": {"S": "A delicious chocolate cake"},
                "prices": {
                    "L": [
                        {"M": {"size": {"S": "6in"}, "base": {"N": "10.00"}}},
                        {"M": {"size": {"S": "8in"}, "base": {"N": "15.00"}}},
                        {"M": {"size": {"S": "10in"}, "base": {"N": "20.00"}}},
                    ]
                },
                "dessert_type": {"S": "cake"},
                "ingredients": {
                    "L": [
                        {"S": "flour"},
                        {"S": "sugar"},
                        {"S": "cocoa"},
                        {"S": "butter"},
                        {"S": "eggs"},
                    ]
                },
                "visible": {"BOOL": False},
                "created_at": {"N": "1711108800"},
                "last_updated_at": {"N": "1711108800"},
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
                        },
                        {
                            "M": {
                                "image_id": {
                                    "S": "00000000-0000-0000-0000-000000000003"
                                },
                                "position": {"N": "2"},
                                "url": {
                                    "S": "https://dessert-images.s3.amazonaws.com/00000000-0000-0000-0000-000000000001/00000000-0000-0000-0000-000000000003"
                                },
                                "file_type": {"S": "image/jpeg"},
                            }
                        },
                    ]
                },
            }
        },
        expected_params={
            "TableName": "desserts",
            "Key": {"dessert_id": "00000000-0000-0000-0000-000000000001"},
        },
    )

    s3_stub.add_response(
        "delete_object",
        {},
        expected_params={
            "Bucket": "dessert-images",
            "Key": "00000000-0000-0000-0000-000000000001/00000000-0000-0000-0000-000000000002",
        },
    )

    s3_stub.add_response(
        "delete_object",
        {},
        expected_params={
            "Bucket": "dessert-images",
            "Key": "00000000-0000-0000-0000-000000000001/00000000-0000-0000-0000-000000000003",
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
            "prices": [
                {"size": "6in", "base": 10.00},
                {"size": "8in", "base": 15.00},
                {"size": "10in", "base": 20.00},
            ],
            "dessert_type": "cake",
            "ingredients": ["flour", "sugar", "cocoa", "butter", "eggs"],
            "visible": False,
            "created_at": 1711108800,
            "last_updated_at": 1711108800,
            "images": [
                {
                    "image_id": "00000000-0000-0000-0000-000000000002",
                    "position": 1,
                    "url": "https://dessert-images.s3.amazonaws.com/00000000-0000-0000-0000-000000000001/00000000-0000-0000-0000-000000000002",
                    "file_type": "image/jpeg",
                },
                {
                    "image_id": "00000000-0000-0000-0000-000000000003",
                    "position": 2,
                    "url": "https://dessert-images.s3.amazonaws.com/00000000-0000-0000-0000-000000000001/00000000-0000-0000-0000-000000000003",
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
