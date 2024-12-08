import unittest
import uuid
from decimal import Decimal
from unittest.mock import MagicMock, call, patch

import pytest
from botocore.stub import Stubber
from fastapi.testclient import TestClient
from freezegun import freeze_time

from src.api import app
from src.routes.post_dessert import desserts_table, dessert_type_count_table

test_client = TestClient(app)


@pytest.fixture(autouse=True)
def monkeypatch_env(monkeypatch):
    monkeypatch.setenv("DYNAMODB_REGION", "us-east-1")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_URL", "http://localhost:8000")
    monkeypatch.setenv("DYNAMODB_DESSERTS_TABLE_NAME", "desserts")
    monkeypatch.setenv("DYNAMODB_PRICES_TABLE_NAME", "prices")
    monkeypatch.setenv("DYNAMODB_DESSERT_TYPE_COUNT_TABLE_NAME", "dessert_type_count")
    monkeypatch.setenv("DESSERT_IMAGES_BUCKET_NAME", "dessert-images")
    monkeypatch.setenv("REGION", "us-east-1")


@pytest.fixture(autouse=True, scope="function")
def desserts_dynamodb_stub():
    with Stubber(desserts_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


@pytest.fixture(autouse=True, scope="function")
def desserts_type_count_dynamodb_stub():
    with Stubber(dessert_type_count_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


@freeze_time("2024-12-12 12:00:00")
@patch(
    "src.routes.post_dessert.s3_client.generate_presigned_url",
    return_value="https://example.com/upload-url",
)
@patch("src.routes.post_dessert.prices_table")
@patch(
    "uuid.uuid4",
    side_effect=[
        uuid.UUID("00000000-0000-0000-0000-000000000002"),
        uuid.UUID("00000000-0000-0000-0000-000000000003"),
    ],
)
def test_handler_valid_event_existing_dessert_type(
    mock_uuid,
    mock_prices_table,
    mock_s3_client,
    desserts_dynamodb_stub,
    desserts_type_count_dynamodb_stub,
):
    mock_batch_writer = MagicMock()
    mock_prices_table.batch_writer.__enter__.return_value = mock_batch_writer

    desserts_type_count_dynamodb_stub.add_response(
        "get_item",
        {"Item": {"dessert_type": {"S": "DESSERT"}, "dessert_count": {"S": "1"}}},
        expected_params={
            "Key": {"dessert_type": "DESSERT"},
            "TableName": "dessert_type_count",
        },
    )

    desserts_type_count_dynamodb_stub.add_response(
        "update_item",
        {"Attributes": {"dessert_count": {"S": "2"}}},
        expected_params={
            "Key": {"dessert_type": "DESSERT"},
            "TableName": "dessert_type_count",
            "UpdateExpression": "set dessert_count = dessert_count + :incr",
            "ExpressionAttributeValues": {":incr": 1},
            "ReturnValues": "ALL_NEW",
        },
    )

    desserts_dynamodb_stub.add_response(
        "put_item",
        {},
        expected_params={
            "Item": {
                "dessert_id": "DESSERT-2",
                "name": "Chocolate Cake",
                "description": "A delicious chocolate cake",
                "dessert_type": "cake",
                "created_at": 1734004800,
                "last_updated_at": 1734004800,
                "visible": False,
                "prices": [
                    {
                        "dessert_id": "DESSERT-2",
                        "size": "slice",
                        "base_price": Decimal(5.00),
                        "discount": Decimal(0.00),
                    },
                    {
                        "dessert_id": "DESSERT-2",
                        "size": "whole",
                        "base_price": Decimal(40.00),
                        "discount": Decimal(0.00),
                    },
                ],
                "ingredients": ["flour", "sugar", "cocoa", "butter", "eggs"],
                "images": [
                    {
                        "image_id": "00000000-0000-0000-0000-000000000002",
                        "url": "https://dessert-images.s3.amazonaws.com/DESSERT-2/00000000-0000-0000-0000-000000000002",
                        "upload_url": "https://example.com/upload-url",
                        "position": 1,
                        "file_name": "image1.jpg",
                        "file_type": "image/jpeg",
                    },
                    {
                        "image_id": "00000000-0000-0000-0000-000000000003",
                        "url": "https://dessert-images.s3.amazonaws.com/DESSERT-2/00000000-0000-0000-0000-000000000003",
                        "upload_url": "https://example.com/upload-url",
                        "position": 2,
                        "file_name": "image2.jpg",
                        "file_type": "image/jpeg",
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
                    "position": 1,
                    "file_name": "image1.jpg",
                    "file_type": "image/jpeg",
                },
                {
                    "position": 2,
                    "file_name": "image2.jpg",
                    "file_type": "image/jpeg",
                },
            ],
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        201,
        {
            "dessert_id": "DESSERT-2",
            "name": "Chocolate Cake",
            "description": "A delicious chocolate cake",
            "dessert_type": "cake",
            "created_at": 1734004800,
            "last_updated_at": 1734004800,
            "visible": False,
            "prices": [
                {
                    "dessert_id": "DESSERT-2",
                    "size": "slice",
                    "base_price": 5.00,
                    "discount": 0.00,
                },
                {
                    "dessert_id": "DESSERT-2",
                    "size": "whole",
                    "base_price": 40.00,
                    "discount": 0.00,
                },
            ],
            "ingredients": ["flour", "sugar", "cocoa", "butter", "eggs"],
            "images": [
                {
                    "image_id": "00000000-0000-0000-0000-000000000002",
                    "url": "https://dessert-images.s3.amazonaws.com/DESSERT-2/00000000-0000-0000-0000-000000000002",
                    "upload_url": "https://example.com/upload-url",
                    "position": 1,
                    "file_name": "image1.jpg",
                    "file_type": "image/jpeg",
                },
                {
                    "image_id": "00000000-0000-0000-0000-000000000003",
                    "url": "https://dessert-images.s3.amazonaws.com/DESSERT-2/00000000-0000-0000-0000-000000000003",
                    "upload_url": "https://example.com/upload-url",
                    "position": 2,
                    "file_name": "image2.jpg",
                    "file_type": "image/jpeg",
                },
            ],
        },
    )


@freeze_time("2024-12-12 12:00:00")
@patch(
    "src.routes.post_dessert.s3_client.generate_presigned_url",
    return_value="https://example.com/upload-url",
)
@patch("src.routes.post_dessert.prices_table")
@patch(
    "uuid.uuid4",
    side_effect=[
        uuid.UUID("00000000-0000-0000-0000-000000000002"),
        uuid.UUID("00000000-0000-0000-0000-000000000003"),
    ],
)
def test_handler_valid_event_new_dessert_type(
    mock_uuid,
    mock_prices_table,
    mock_s3_client,
    desserts_dynamodb_stub,
    desserts_type_count_dynamodb_stub,
):
    mock_batch_writer = MagicMock()
    mock_prices_table.batch_writer.__enter__.return_value = mock_batch_writer

    desserts_type_count_dynamodb_stub.add_response(
        "get_item",
        {},
        expected_params={
            "Key": {"dessert_type": "DESSERT"},
            "TableName": "dessert_type_count",
        },
    )

    desserts_type_count_dynamodb_stub.add_response(
        "put_item",
        {},
        expected_params={
            "Item": {"dessert_type": "DESSERT", "dessert_count": 1},
            "TableName": "dessert_type_count",
        },
    )

    desserts_dynamodb_stub.add_response(
        "put_item",
        {},
        expected_params={
            "Item": {
                "dessert_id": "DESSERT-1",
                "name": "Chocolate Cake",
                "description": "A delicious chocolate cake",
                "dessert_type": "cake",
                "created_at": 1734004800,
                "last_updated_at": 1734004800,
                "visible": False,
                "prices": [
                    {
                        "dessert_id": "DESSERT-1",
                        "size": "slice",
                        "base_price": Decimal(5.00),
                        "discount": Decimal(0.00),
                    },
                    {
                        "dessert_id": "DESSERT-1",
                        "size": "whole",
                        "base_price": Decimal(40.00),
                        "discount": Decimal(0.00),
                    },
                ],
                "ingredients": ["flour", "sugar", "cocoa", "butter", "eggs"],
                "images": [
                    {
                        "image_id": "00000000-0000-0000-0000-000000000002",
                        "url": "https://dessert-images.s3.amazonaws.com/DESSERT-1/00000000-0000-0000-0000-000000000002",
                        "upload_url": "https://example.com/upload-url",
                        "position": 1,
                        "file_name": "image1.jpg",
                        "file_type": "image/jpeg",
                    },
                    {
                        "image_id": "00000000-0000-0000-0000-000000000003",
                        "url": "https://dessert-images.s3.amazonaws.com/DESSERT-1/00000000-0000-0000-0000-000000000003",
                        "upload_url": "https://example.com/upload-url",
                        "position": 2,
                        "file_name": "image2.jpg",
                        "file_type": "image/jpeg",
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
                    "position": 1,
                    "file_name": "image1.jpg",
                    "file_type": "image/jpeg",
                },
                {
                    "position": 2,
                    "file_name": "image2.jpg",
                    "file_type": "image/jpeg",
                },
            ],
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        201,
        {
            "dessert_id": "DESSERT-1",
            "name": "Chocolate Cake",
            "description": "A delicious chocolate cake",
            "dessert_type": "cake",
            "created_at": 1734004800,
            "last_updated_at": 1734004800,
            "visible": False,
            "prices": [
                {
                    "dessert_id": "DESSERT-1",
                    "size": "slice",
                    "base_price": 5.00,
                    "discount": 0.00,
                },
                {
                    "dessert_id": "DESSERT-1",
                    "size": "whole",
                    "base_price": 40.00,
                    "discount": 0.00,
                },
            ],
            "ingredients": ["flour", "sugar", "cocoa", "butter", "eggs"],
            "images": [
                {
                    "image_id": "00000000-0000-0000-0000-000000000002",
                    "url": "https://dessert-images.s3.amazonaws.com/DESSERT-1/00000000-0000-0000-0000-000000000002",
                    "upload_url": "https://example.com/upload-url",
                    "position": 1,
                    "file_name": "image1.jpg",
                    "file_type": "image/jpeg",
                },
                {
                    "image_id": "00000000-0000-0000-0000-000000000003",
                    "url": "https://dessert-images.s3.amazonaws.com/DESSERT-1/00000000-0000-0000-0000-000000000003",
                    "upload_url": "https://example.com/upload-url",
                    "position": 2,
                    "file_name": "image2.jpg",
                    "file_type": "image/jpeg",
                },
            ],
        },
    )
