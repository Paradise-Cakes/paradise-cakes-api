import pytest
from freezegun import freeze_time
from botocore.stub import Stubber
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
                "created_at": "2024-03-22T12:00:00",
                "last_updated_at": "2024-03-22T12:00:00",
                "name": "https://example.com/image.jpg",
                "position": 1,
            },
            "TableName": "dessert_images",
        },
    )

    response = test_client.post(
        "/desserts/00000000-0000-0000-0000-000000000002/images",
        json={
            "name": "https://example.com/image.jpg",
            "position": 1,
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        201,
        {
            "image_id": "00000000-0000-0000-0000-000000000001",
            "dessert_id": "00000000-0000-0000-0000-000000000002",
            "created_at": "2024-03-22T12:00:00",
            "last_updated_at": "2024-03-22T12:00:00",
            "name": "https://example.com/image.jpg",
            "position": 1,
            "upload_url": "https://dessert-images.s3.amazonaws.com/00000000-0000-0000-0000-000000000002/00000000-0000-0000-0000-000000000001?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=fakekey%2F20240322%2Ftest%2Fs3%2Faws4_request&X-Amz-Date=20240322T120000Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Security-Token=fake&X-Amz-Signature=09ef368014778ab3d1e379c63fb65c64e12b6653bc93b2890974a61ef27a443b",
        },
    )
