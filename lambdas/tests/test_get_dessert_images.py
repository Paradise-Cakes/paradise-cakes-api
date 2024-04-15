import pytest
from botocore.stub import Stubber
from fastapi.testclient import TestClient
from src.api import app
from src.routes.get_dessert_images import dessert_images_table
from src.models import DessertImage


test_client = TestClient(app)


@pytest.fixture(autouse=True, scope="function")
def dessert_images_dynamodb_stub():
    with Stubber(dessert_images_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


def test_handler_get_dessert_images(dessert_images_dynamodb_stub):
    dessert_images_dynamodb_stub.add_response(
        "query",
        {
            "Items": [
                {
                    "image_id": {"S": "00000000-0000-0000-0000-000000000001"},
                    "dessert_id": {"S": "00000000-0000-0000-0000-000000000002"},
                    "created_at": {"N": "1711108800"},
                    "last_updated_at": {"N": "1711108800"},
                    "position": {"N": "2"},
                    "url": {
                        "S": "https://dessert-images.s3.amazonaws.com/00000000-0000-0000-0000-000000000002/00000000-0000-0000-0000-000000000001.jpg"
                    },
                    "file_extension": {"S": "jpg"},
                },
                {
                    "image_id": {"S": "00000000-0000-0000-0000-000000000001"},
                    "dessert_id": {"S": "00000000-0000-0000-0000-000000000002"},
                    "created_at": {"N": "1711108800"},
                    "last_updated_at": {"N": "1711108800"},
                    "position": {"N": "1"},
                    "url": {
                        "S": "https://dessert-images.s3.amazonaws.com/00000000-0000-0000-0000-000000000002/00000000-0000-0000-0000-000000000001.jpg"
                    },
                    "file_extension": {"S": "jpg"},
                },
            ]
        },
        expected_params={
            "KeyConditionExpression": "dessert_id = :dessert_id",
            "ExpressionAttributeValues": {
                ":dessert_id": "00000000-0000-0000-0000-000000000002"
            },
            "TableName": "dessert_images",
        },
    )

    response = test_client.get("/desserts/00000000-0000-0000-0000-000000000002/images")

    pytest.helpers.assert_responses_equal(
        response,
        200,
        [
            {
                "image_id": "00000000-0000-0000-0000-000000000001",
                "dessert_id": "00000000-0000-0000-0000-000000000002",
                "created_at": 1711108800,
                "last_updated_at": 1711108800,
                "position": 1,
                "url": "https://dessert-images.s3.amazonaws.com/00000000-0000-0000-0000-000000000002/00000000-0000-0000-0000-000000000001.jpg",
                "file_extension": "jpg",
            },
            {
                "image_id": "00000000-0000-0000-0000-000000000001",
                "dessert_id": "00000000-0000-0000-0000-000000000002",
                "created_at": 1711108800,
                "last_updated_at": 1711108800,
                "position": 2,
                "url": "https://dessert-images.s3.amazonaws.com/00000000-0000-0000-0000-000000000002/00000000-0000-0000-0000-000000000001.jpg",
                "file_extension": "jpg",
            },
        ],
    )


def test_handler_get_dessert_images_no_images(dessert_images_dynamodb_stub):
    dessert_images_dynamodb_stub.add_response(
        "query",
        {},
        expected_params={
            "KeyConditionExpression": "dessert_id = :dessert_id",
            "ExpressionAttributeValues": {
                ":dessert_id": "00000000-0000-0000-0000-000000000002"
            },
            "TableName": "dessert_images",
        },
    )

    response = test_client.get("/desserts/00000000-0000-0000-0000-000000000002/images")

    pytest.helpers.assert_responses_equal(response, 200, [])
