import pytest
from freezegun import freeze_time
from botocore.stub import Stubber
from fastapi.testclient import TestClient
from src.api import app
from src.routes.get_desserts import desserts_table

test_client = TestClient(app)


@pytest.fixture(autouse=True, scope="function")
def desserts_dynamodb_stub():
    with Stubber(desserts_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


@freeze_time("2024-03-22 12:00:00")
def test_handler_valid_event_get_desserts(desserts_dynamodb_stub):
    desserts_dynamodb_stub.add_response(
        "scan",
        {
            "Items": [
                {
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
                    "ingredients": {
                        "L": [
                            {"S": "flour"},
                            {"S": "sugar"},
                            {"S": "cocoa"},
                            {"S": "butter"},
                            {"S": "eggs"},
                        ]
                    },
                },
                {
                    "dessert_id": {"S": "DESSERT-2"},
                    "name": {"S": "Cheesecake"},
                    "description": {"S": "A delicious cheesecake"},
                    "prices": {
                        "L": [
                            {"M": {"size": {"S": "6in"}, "base": {"N": "12.00"}}},
                            {"M": {"size": {"S": "8in"}, "base": {"N": "18.00"}}},
                            {"M": {"size": {"S": "10in"}, "base": {"N": "24.00"}}},
                        ]
                    },
                    "dessert_type": {"S": "cake"},
                    "ingredients": {
                        "L": [
                            {"S": "cream cheese"},
                            {"S": "sugar"},
                            {"S": "eggs"},
                            {"S": "vanilla"},
                        ]
                    },
                    "visible": {"BOOL": False},
                },
            ]
        },
        expected_params={"TableName": "desserts"},
    )

    response = test_client.get("/desserts?dessert_type=cake")

    pytest.helpers.assert_responses_equal(
        response,
        200,
        [
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
                "ingredients": ["flour", "sugar", "cocoa", "butter", "eggs"],
                "visible": False,
            },
            {
                "dessert_id": "DESSERT-2",
                "name": "Cheesecake",
                "description": "A delicious cheesecake",
                "prices": [
                    {"size": "6in", "base": 12.00},
                    {"size": "8in", "base": 18.00},
                    {"size": "10in", "base": 24.00},
                ],
                "dessert_type": "cake",
                "ingredients": ["cream cheese", "sugar", "eggs", "vanilla"],
                "visible": False,
            },
        ],
    )


@freeze_time("2024-03-22 12:00:00")
def test_handler_valid_event_get_desserts_no_items(desserts_dynamodb_stub):
    desserts_dynamodb_stub.add_response(
        "scan",
        {},
        expected_params={"TableName": "desserts"},
    )

    response = test_client.get("/desserts?dessert_type=cake")

    pytest.helpers.assert_responses_equal(
        response, 404, {"detail": "No desserts found"}
    )
