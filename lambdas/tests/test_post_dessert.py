import uuid
from decimal import Decimal
from unittest.mock import patch

import pytest
from botocore.stub import Stubber
from fastapi.testclient import TestClient
from freezegun import freeze_time

from src.api import app
from src.routes.post_dessert import desserts_table

test_client = TestClient(app)


@pytest.fixture(autouse=True, scope="function")
def desserts_dynamodb_stub():
    with Stubber(desserts_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


@freeze_time("2024-03-22 12:00:00")
@patch("uuid.uuid4", return_value=uuid.UUID("00000000-0000-0000-0000-000000000001"))
def test_handler_add_dessert(mock_uuid, desserts_dynamodb_stub):
    desserts_dynamodb_stub.add_response(
        "put_item",
        {},
        expected_params={
            "Item": {
                "dessert_id": "00000000-0000-0000-0000-000000000001",
                "name": "chocolate cake",
                "description": "a delicious chocolate cake",
                "prices": [
                    {"size": "small", "base": Decimal("10.00")},
                    {"size": "large", "base": Decimal("20.00")},
                ],
                "dessert_type": "cake",
                "ingredients": ["chocolate", "flour", "sugar"],
                "created_at": 1711108800,
                "last_updated_at": 1711108800,
                "visible": False,
            },
            "TableName": "desserts",
        },
    )

    response = test_client.post(
        "/desserts",
        json={
            "name": "chocolate cake",
            "description": "a delicious chocolate cake",
            "prices": [
                {"size": "small", "base": 10.00},
                {"size": "large", "base": 20.00},
            ],
            "dessert_type": "cake",
            "ingredients": ["chocolate", "flour", "sugar"],
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        201,
        {
            "dessert_id": "00000000-0000-0000-0000-000000000001",
            "name": "chocolate cake",
            "description": "a delicious chocolate cake",
            "prices": [
                {"size": "small", "base": 10.00},
                {"size": "large", "base": 20.00},
            ],
            "dessert_type": "cake",
            "ingredients": ["chocolate", "flour", "sugar"],
            "created_at": 1711108800,
            "last_updated_at": 1711108800,
            "visible": False,
        },
    )
