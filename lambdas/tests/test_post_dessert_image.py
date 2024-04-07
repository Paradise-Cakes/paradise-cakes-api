import pytest
from freezegun import freeze_time
from botocore.stub import Stubber, ANY
from unittest.mock import patch
from fastapi.testclient import TestClient
from src.api import app
from src.routes.post_dessert_image import dessert_images_table, s3_client
from io import BytesIO

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


@pytest.fixture(autouse=True, scope="function")
def s3_client_stub():
    with Stubber(s3_client) as s3_stubber:
        yield s3_stubber
        s3_stubber.assert_no_pending_responses()


@freeze_time("2024-03-22 12:00:00")
@patch("uuid.uuid4", return_value="00000000-0000-0000-0000-000000000001")
def test_handler_create_image(mock_uuid, s3_client_stub, dessert_images_dynamodb_stub):
    s3_client_stub.add_response(
        "put_object",
        {},
        expected_params={
            "Bucket": "dessert-images",
            "Key": "00000000-0000-0000-0000-000000000001.jpg",
            "Body": ANY,
        },
    )

    dessert_images_dynamodb_stub.add_response(
        "put_item",
        {},
        expected_params={
            "Item": {
                "image_id": "00000000-0000-0000-0000-000000000001",
                "dessert_id": "00000000-0000-0000-0000-000000000002",
                "created_at": "2024-03-22T12:00:00",
                "last_updated_at": "2024-03-22T12:00:00",
                "position": 1,
                "file_url": "https://dessert-images.s3.amazonaws.com/00000000-0000-0000-0000-000000000002/00000000-0000-0000-0000-000000000001.jpg",
            },
            "TableName": "dessert_images",
        },
    )

    files = {
        "file": ("filename.jpg", BytesIO(b"fake image data"), "image/jpeg"),
    }
    response = test_client.post(
        "/desserts/00000000-0000-0000-0000-000000000002/images",
        files=files,
        data={"position": 1},  # Sending position as form data
    )

    pytest.helpers.assert_responses_equal(
        response,
        201,
        {
            "image_id": "00000000-0000-0000-0000-000000000001",
            "dessert_id": "00000000-0000-0000-0000-000000000002",
            "created_at": "2024-03-22T12:00:00",
            "last_updated_at": "2024-03-22T12:00:00",
            "position": 1,
            "file_url": "https://dessert-images.s3.amazonaws.com/00000000-0000-0000-0000-000000000002/00000000-0000-0000-0000-000000000001.jpg",
        },
    )


@freeze_time("2024-03-22 12:00:00")
@patch("uuid.uuid4", return_value="00000000-0000-0000-0000-000000000001")
def test_handler_s3_upload_exception(mock_uuid, s3_client_stub):
    s3_client_stub.add_client_error(
        "put_object",
        service_error_code="InternalError",
        http_status_code=500,
        expected_params={
            "Bucket": "dessert-images",
            "Key": "00000000-0000-0000-0000-000000000001.jpg",
            "Body": ANY,
        },
    )

    response = test_client.post(
        "/desserts/00000000-0000-0000-0000-000000000002/images",
        files={
            "file": ("filename.jpg", BytesIO(b"fake image data"), "image/jpeg"),
        },
        data={"position": 1},
    )

    pytest.helpers.assert_responses_equal(
        response,
        500,
        {"detail": "Error uploading file to S3"},
    )
