import pytest
from boto3.dynamodb.conditions import Key
from botocore.stub import Stubber
from fastapi.testclient import TestClient
from freezegun import freeze_time

from src.api import app
from src.routes.get_desserts import desserts_table, dynamodb_client

test_client = TestClient(app)


@pytest.fixture(autouse=True, scope="function")
def desserts_dynamodb_stub():
    with Stubber(desserts_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


@pytest.fixture(autouse=True, scope="function")
def dynamo_stub():
    with Stubber(dynamodb_client) as dynamo_stubber:
        yield dynamo_stubber
        dynamo_stubber.assert_no_pending_responses()


@freeze_time("2024-03-22 12:00:00")
def test_handler_valid_event_get_desserts_of_dessert_type(
    desserts_dynamodb_stub, dynamo_stub
):
    desserts_dynamodb_stub.add_response(
        "query",
        {
            "Items": [
                {
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
                                    "file_name": {"S": "image1.jpg"},
                                    "file_type": {"S": "jpg"},
                                }
                            },
                            {
                                "M": {
                                    "image_id": {"S": "IMAGE-2"},
                                    "url": {"S": "https://example.com/image2.jpg"},
                                    "position": {"N": "2"},
                                    "file_name": {"S": "image2.jpg"},
                                    "file_type": {"S": "jpg"},
                                }
                            },
                        ]
                    },
                },
                {
                    "dessert_id": {"S": "DESSERT-2"},
                    "name": {"S": "Vanilla Cake"},
                    "description": {"S": "A delicious vanilla cake"},
                    "dessert_type": {"S": "cake"},
                    "created_at": {"N": "1711108800"},
                    "last_updated_at": {"N": "1711108800"},
                    "visible": {"BOOL": False},
                    "ingredients": {
                        "L": [
                            {"S": "flour"},
                            {"S": "sugar"},
                            {"S": "butter"},
                            {"S": "eggs"},
                        ]
                    },
                    "images": {
                        "L": [
                            {
                                "M": {
                                    "image_id": {"S": "IMAGE-3"},
                                    "url": {"S": "https://example.com/image3.jpg"},
                                    "position": {"N": "1"},
                                    "file_name": {"S": "image3.jpg"},
                                    "file_type": {"S": "jpg"},
                                }
                            },
                            {
                                "M": {
                                    "image_id": {"S": "IMAGE-4"},
                                    "url": {"S": "https://example.com/image4.jpg"},
                                    "position": {"N": "2"},
                                    "file_name": {"S": "image4.jpg"},
                                    "file_type": {"S": "jpg"},
                                }
                            },
                        ]
                    },
                },
            ]
        },
        expected_params={
            "TableName": "desserts",
            "IndexName": "dessert_type_index",
            "KeyConditionExpression": Key("dessert_type").eq("cake"),
        },
    )

    dynamo_stub.add_response(
        "batch_get_item",
        {
            "Responses": {
                "prices": [
                    {
                        "dessert_id": {"S": "DESSERT-1"},
                        "size": {"S": "6in"},
                        "base_price": {"N": "10.00"},
                        "discount": {"N": "0.00"},
                    },
                    {
                        "dessert_id": {"S": "DESSERT-2"},
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
                ]
            }
        },
        expected_params={
            "RequestItems": {
                "prices": {
                    "Keys": [
                        {"dessert_id": {"S": "DESSERT-1"}},
                        {"dessert_id": {"S": "DESSERT-2"}},
                    ]
                }
            }
        },
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
                ],
                "ingredients": ["flour", "sugar", "cocoa", "butter", "eggs"],
                "images": [
                    {
                        "image_id": "IMAGE-1",
                        "url": "https://example.com/image1.jpg",
                        "position": 1,
                        "file_name": "image1.jpg",
                        "file_type": "jpg",
                    },
                    {
                        "image_id": "IMAGE-2",
                        "url": "https://example.com/image2.jpg",
                        "position": 2,
                        "file_name": "image2.jpg",
                        "file_type": "jpg",
                    },
                ],
            },
            {
                "dessert_id": "DESSERT-2",
                "name": "Vanilla Cake",
                "description": "A delicious vanilla cake",
                "dessert_type": "cake",
                "created_at": 1711108800,
                "last_updated_at": 1711108800,
                "visible": False,
                "prices": [
                    {
                        "dessert_id": "DESSERT-2",
                        "size": "6in",
                        "base_price": 10.00,
                        "discount": 0.00,
                    }
                ],
                "ingredients": ["flour", "sugar", "butter", "eggs"],
                "images": [
                    {
                        "image_id": "IMAGE-3",
                        "url": "https://example.com/image3.jpg",
                        "position": 1,
                        "file_name": "image3.jpg",
                        "file_type": "jpg",
                    },
                    {
                        "image_id": "IMAGE-4",
                        "url": "https://example.com/image4.jpg",
                        "position": 2,
                        "file_name": "image4.jpg",
                        "file_type": "jpg",
                    },
                ],
            },
        ],
    )


@freeze_time("2024-03-22 12:00:00")
def test_handler_valid_event_no_desserts_of_dessert_type(desserts_dynamodb_stub):
    desserts_dynamodb_stub.add_response(
        "query",
        {"Items": []},
        expected_params={
            "TableName": "desserts",
            "IndexName": "dessert_type_index",
            "KeyConditionExpression": Key("dessert_type").eq("cake"),
        },
    )

    response = test_client.get("/desserts?dessert_type=cake")

    pytest.helpers.assert_responses_equal(
        response, 404, {"detail": "No desserts found of type cake"}
    )
