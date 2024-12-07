import uuid
from decimal import Decimal
import unittest
from unittest.mock import patch, MagicMock, call

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
@patch("src.routes.post_dessert.prices_table")
@patch("uuid.uuid4", return_value=uuid.UUID("00000000-0000-0000-0000-000000000001"))
def test_handler_add_dessert(mock_uuid, mock_prices_table, desserts_dynamodb_stub):
    mock_batch_writer = MagicMock()
    mock_prices_table.batch_writer.__enter__.return_value = mock_batch_writer

    desserts_dynamodb_stub.add_response(
        "put_item",
        {},
        expected_params={
            "Item": {
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
                        "size": "slice",
                        "base_price": Decimal(5.00),
                        "discount": Decimal(0.00),
                    },
                    {
                        "dessert_id": "00000000-0000-0000-0000-000000000001",
                        "size": "whole",
                        "base_price": Decimal(40.00),
                        "discount": Decimal(0.00),
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
            "TableName": "desserts",
        },
    )

    response = test_client.post(
        "/desserts",
        json={
            "name": "Chocolate Cake",
            "description": "A delicious chocolate cake",
            "dessert_type": "cake",
            "prices": [
                {"size": "slice", "base_price": 5.00, "discount": 0.00},
                {"size": "whole", "base_price": 40.00, "discount": 0.00},
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

    pytest.helpers.assert_responses_equal(
        response,
        201,
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
                    "size": "slice",
                    "base_price": 5.00,
                    "discount": 0.00,
                },
                {
                    "dessert_id": "00000000-0000-0000-0000-000000000001",
                    "size": "whole",
                    "base_price": 40.00,
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
