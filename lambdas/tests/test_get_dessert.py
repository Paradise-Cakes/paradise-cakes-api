import pytest
from freezegun import freeze_time
from botocore.stub import Stubber
from fastapi.testclient import TestClient
import app
from src.routes.get_dessert import desserts_table

test_client = TestClient(app)


@pytest.fixture(autouse=True, scope="function")
def desserts_dynamodb_stub():
    with Stubber(desserts_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


@freeze_time("2024-03-22 12:00:00")
def test_handler_valid_event_get_dessert(desserts_dynamodb_stub):
    desserts_dynamodb_stub.add_response(
        "get_item",
        {
            "Item": {
                "dessert_id": {"S": "DESSERT-1"},
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
                "image_urls": {
                    "L": [
                        {"M": {"uri": {"S": "https://example.com/chocolate-cake.jpg"}}}
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
            }
        },
        expected_params={
            "TableName": "desserts",
            "Key": {"dessert_id": "DESSERT-1"},
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
            "prices": [
                {"size": "6in", "base": 10.00},
                {"size": "8in", "base": 15.00},
                {"size": "10in", "base": 20.00},
            ],
            "dessert_type": "cake",
            "image_urls": [{"uri": "https://example.com/chocolate-cake.jpg"}],
            "ingredients": ["flour", "sugar", "cocoa", "butter", "eggs"],
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
