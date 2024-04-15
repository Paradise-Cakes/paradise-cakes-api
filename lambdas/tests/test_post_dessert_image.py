import pytest
from freezegun import freeze_time
from botocore.stub import Stubber, ANY
from unittest.mock import patch
from fastapi.testclient import TestClient
from src.api import app
from src.routes.post_dessert_image import dessert_images_table

test_client = TestClient(app)


@pytest.fixture(autouse=True)
def monkeypatch_env(monkeypatch):
    monkeypatch.setenv("DYNAMODB_REGION", "us-east-1")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_URL", None)
    monkeypatch.setenv("DYNAMODB_DESSERT_IMAGES_TABLE_NAME", "dessert_images")
    monkeypatch.setenv("DESSERT_IMAGES_BUCKET_NAME", "dessert-images")
    monkeypatch.setenv("REGION", "us-east-1")


@pytest.fixture(autouse=True, scope="function")
def dessert_images_dynamodb_stub():
    with Stubber(dessert_images_table.meta.client) as ddb_stubber:
        yield ddb_stubber
        ddb_stubber.assert_no_pending_responses()


@freeze_time("2024-03-22 12:00:00")
@patch("uuid.uuid4", return_value="00000000-0000-0000-0000-000000000001")
def test_handler_create_image(mock_uuid, dessert_images_dynamodb_stub):
    dessert_images_dynamodb_stub.add_response(
        "put_item",
        {},
        expected_params={
            "Item": {
                "image_id": "00000000-0000-0000-0000-000000000001",
                "dessert_id": "00000000-0000-0000-0000-000000000002",
                "position": 1,
                "created_at": 1711108800,
                "last_updated_at": 1711108800,
                "file_extension": "jpg",
                "url": "https://dessert-images.s3.us-east-1.amazonaws.com/00000000-0000-0000-0000-000000000001.jpg",
            },
            "TableName": "dessert_images",
        },
    )

    response = test_client.post(
        "/desserts/00000000-0000-0000-0000-000000000002/images",
        json={"position": 1, "file_extension": "jpg"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        200,
        {},
    )
