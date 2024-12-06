from decimal import Decimal
from unittest.mock import patch

import pytest
from botocore.stub import Stubber
from fastapi.testclient import TestClient
from freezegun import freeze_time

from src.api import app
from src.routes.patch_dessert import desserts_table

test_client = TestClient(app)


@pytest.fixture(autouse=True, scope="function")
def desserts_dynamodb_stub():
    with Stubber(desserts_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


@freeze_time("2024-03-22 12:00:00")
def test_handler_patch_dessert(desserts_dynamodb_stub):
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
            }
        },
        expected_params={
            "TableName": "desserts",
            "Key": {"dessert_id": "00000000-0000-0000-0000-000000000001"},
        },
    )
    desserts_dynamodb_stub.add_response(
        "update_item",
        {
            "Attributes": {
                "dessert_id": {"S": "00000000-0000-0000-0000-000000000001"},
                "name": {"S": "Chocolate Cake"},
                "description": {"S": "A delicious chocolate cake"},
                "prices": {
                    "L": [
                        {"M": {"size": {"S": "6in"}, "base": {"N": "100.00"}}},
                        {"M": {"size": {"S": "8in"}, "base": {"N": "15.00"}}},
                        {"M": {"size": {"S": "10in"}, "base": {"N": "20.00"}}},
                    ]
                },
                "created_at": {"N": "1711108800"},
                "last_updated_at": {"N": "1711108800"},
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
                "visible": {"BOOL": True},
            }
        },
        expected_params={
            "Key": {"dessert_id": "00000000-0000-0000-0000-000000000001"},
            "ReturnValues": "ALL_NEW",
            "UpdateExpression": "SET #prices = :prices, #visible = :visible, #last_updated_at = :last_updated_at",
            "ExpressionAttributeNames": {
                "#last_updated_at": "last_updated_at",
                "#visible": "visible",
                "#prices": "prices",
            },
            "ExpressionAttributeValues": {
                ":last_updated_at": 1711108800,
                ":visible": True,
                ":prices": [
                    {"size": "6in", "base": Decimal(100.00).quantize(Decimal("0.01"))},
                ],
            },
            "TableName": "desserts",
        },
    )

    response = test_client.patch(
        "/desserts/00000000-0000-0000-0000-000000000001",
        json={"visible": True, "prices": [{"size": "6in", "base": 100.00}]},
    )

    pytest.helpers.assert_responses_equal(
        response,
        200,
        {
            "dessert_id": "00000000-0000-0000-0000-000000000001",
            "name": "Chocolate Cake",
            "description": "A delicious chocolate cake",
            "prices": [
                {"size": "6in", "base": 100.00},
                {"size": "8in", "base": 15.00},
                {"size": "10in", "base": 20.00},
            ],
            "dessert_type": "cake",
            "ingredients": ["flour", "sugar", "cocoa", "butter", "eggs"],
            "created_at": 1711108800,
            "last_updated_at": 1711108800,
            "visible": True,
        },
    )


@freeze_time("2024-03-22 12:00:00")
def test_handler_patch_dessert_not_found(desserts_dynamodb_stub):
    desserts_dynamodb_stub.add_response(
        "get_item",
        {},
        expected_params={
            "TableName": "desserts",
            "Key": {"dessert_id": "00000000-0000-0000-0000-000000000001"},
        },
    )

    response = test_client.patch(
        "/desserts/00000000-0000-0000-0000-000000000001",
        json={"visible": True},
    )

    pytest.helpers.assert_responses_equal(
        response, 404, {"detail": "Dessert not found"}
    )


# @freeze_time("2024-03-22 12:00:00")
# def test_handler_updates_image_position(desserts_dynamodb_stub):
#     desserts_dynamodb_stub.add_response(
#         "get_item",
#         {
#             "Item": {
#                 "dessert_id": {"S": "00000000-0000-0000-0000-000000000001"},
#                 "name": {"S": "Chocolate Cake"},
#                 "description": {"S": "A delicious chocolate cake"},
#                 "prices": {
#                     "L": [
#                         {"M": {"size": {"S": "6in"}, "base": {"N": "10.00"}}},
#                         {"M": {"size": {"S": "8in"}, "base": {"N": "15.00"}}},
#                         {"M": {"size": {"S": "10in"}, "base": {"N": "20.00"}}},
#                     ]
#                 },
#                 "dessert_type": {"S": "cake"},
#                 "ingredients": {
#                     "L": [
#                         {"S": "flour"},
#                         {"S": "sugar"},
#                         {"S": "cocoa"},
#                         {"S": "butter"},
#                         {"S": "eggs"},
#                     ]
#                 },
#                 "visible": {"BOOL": False},
#                 "images": {
#                     "L": [
#                         {
#                             "M": {
#                                 "image_id": {
#                                     "S": "00000000-0000-0000-0000-000000000002"
#                                 },
#                                 "url": {"S": "https://example.com/image.jpg"},
#                                 "position": {"N": "1"},
#                                 "file_type": {"S": "image/jpeg"},
#                             }
#                         },
#                         {
#                             "M": {
#                                 "image_id": {
#                                     "S": "00000000-0000-0000-0000-000000000003"
#                                 },
#                                 "url": {"S": "https://example.com/image.jpg"},
#                                 "position": {"N": "2"},
#                                 "file_type": {"S": "image/jpeg"},
#                             }
#                         },
#                     ]
#                 },
#             }
#         },
#         expected_params={
#             "TableName": "desserts",
#             "Key": {"dessert_id": "00000000-0000-0000-0000-000000000001"},
#         },
#     )
#     desserts_dynamodb_stub.add_response(
#         "update_item",
#         {
#             "Attributes": {
#                 "dessert_id": {"S": "00000000-0000-0000-0000-000000000001"},
#                 "name": {"S": "Chocolate Cake"},
#                 "description": {"S": "A delicious chocolate cake"},
#                 "prices": {
#                     "L": [
#                         {"M": {"size": {"S": "6in"}, "base": {"N": "10.00"}}},
#                         {"M": {"size": {"S": "8in"}, "base": {"N": "15.00"}}},
#                         {"M": {"size": {"S": "10in"}, "base": {"N": "20.00"}}},
#                     ]
#                 },
#                 "created_at": {"N": "1711108800"},
#                 "last_updated_at": {"N": "1711108800"},
#                 "dessert_type": {"S": "cake"},
#                 "ingredients": {
#                     "L": [
#                         {"S": "flour"},
#                         {"S": "sugar"},
#                         {"S": "cocoa"},
#                         {"S": "butter"},
#                         {"S": "eggs"},
#                     ]
#                 },
#                 "visible": {"BOOL": False},
#                 "images": {
#                     "L": [
#                         {
#                             "M": {
#                                 "image_id": {
#                                     "S": "00000000-0000-0000-0000-000000000003"
#                                 },
#                                 "url": {"S": "https://example.com/image.jpg"},
#                                 "position": {"N": "1"},
#                                 "file_type": {"S": "image/jpeg"},
#                             }
#                         },
#                     ]
#                 },
#             }
#         },
#         expected_params={
#             "Key": {"dessert_id": "00000000-0000-0000-0000-000000000001"},
#             "ReturnValues": "ALL_NEW",
#             "UpdateExpression": "SET #images = :images, #last_updated_at = :last_updated_at",
#             "ExpressionAttributeNames": {
#                 "#last_updated_at": "last_updated_at",
#                 "#images": "images",
#             },
#             "ExpressionAttributeValues": {
#                 ":last_updated_at": 1711108800,
#                 ":images": [
#                     {
#                         "file_type": "image/jpeg",
#                         "image_id": "00000000-0000-0000-0000-000000000003",
#                         "position": 1,
#                         "url": "https://example.com/image.jpg",
#                     }
#                 ],
#             },
#             "TableName": "desserts",
#         },
#     )

#     response = test_client.patch(
#         "/desserts/00000000-0000-0000-0000-000000000001",
#         json={
#             "images": [
#                 {
#                     "image_id": "00000000-0000-0000-0000-000000000003",
#                     "position": 1,
#                     "file_type": "image/jpeg",
#                     "url": "https://example.com/image.jpg",
#                 },
#             ]
#         },
#     )

#     pytest.helpers.assert_responses_equal(
#         response,
#         200,
#         {
#             "dessert_id": "00000000-0000-0000-0000-000000000001",
#             "name": "Chocolate Cake",
#             "description": "A delicious chocolate cake",
#             "prices": [
#                 {"size": "6in", "base": 10.00},
#                 {"size": "8in", "base": 15.00},
#                 {"size": "10in", "base": 20.00},
#             ],
#             "dessert_type": "cake",
#             "ingredients": ["flour", "sugar", "cocoa", "butter", "eggs"],
#             "created_at": 1711108800,
#             "last_updated_at": 1711108800,
#             "visible": False,
#             "images": [
#                 {
#                     "image_id": "00000000-0000-0000-0000-000000000002",
#                     "url": "https://example.com/image.jpg",
#                     "position": 2,
#                     "file_type": "image/jpeg",
#                 },
#                 {
#                     "image_id": "00000000-0000-0000-0000-000000000003",
#                     "url": "https://example.com/image.jpg",
#                     "position": 1,
#                     "file_type": "image/jpeg",
#                 },
#             ],
#         },
#     )
