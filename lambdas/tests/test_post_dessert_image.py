import pytest
from freezegun import freeze_time
from botocore.stub import Stubber, ANY
from unittest.mock import patch
from fastapi.testclient import TestClient
from src.api import app
from src.routes.post_dessert_image import desserts_table

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


@freeze_time("2024-03-22 12:00:00")
@patch("uuid.uuid4", return_value="00000000-0000-0000-0000-000000000001")
def test_handler_create_image(mock_uuid, desserts_dynamodb_stub):
    desserts_dynamodb_stub.add_response(
        "update_item",
        {},
        expected_params={
            "TableName": "desserts",
            "Key": {"dessert_id": "00000000-0000-0000-0000-000000000002"},
            "UpdateExpression": "SET images = list_append(if_not_exists(images, :empty_list), :i)",
            "ExpressionAttributeValues": {
                ":empty_list": [],
                ":i": [
                    {
                        "position": 1,
                        "file_type": "image/jpeg",
                        "image_id": "00000000-0000-0000-0000-000000000001",
                        "url": "https://dessert-images.s3.amazonaws.com/00000000-0000-0000-0000-000000000002/00000000-0000-0000-0000-000000000001",
                    }
                ],
            },
        },
    )

    response = test_client.post(
        "/desserts/00000000-0000-0000-0000-000000000002/images",
        json={"position": 1, "file_type": "image/jpeg"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        200,
        {},
    )
