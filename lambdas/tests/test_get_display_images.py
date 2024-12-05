import boto3
import pytest
from botocore.stub import Stubber
from fastapi.testclient import TestClient

from src.api import app
from src.routes.get_display_images import s3_client

client = TestClient(app)


@pytest.fixture(autouse=True)
def set_env_variables(monkeypatch):
    monkeypatch.setenv("DESSERT_IMAGES_BUCKET_NAME", "dessert-images")


@pytest.fixture(autouse=True, scope="function")
def s3_stub():
    with Stubber(s3_client) as s3_stubber:
        yield s3_stubber
        s3_stubber.assert_no_pending_responses()


def test_get_image_urls_empty_bucket(s3_stub):
    s3_stub.add_response(
        "list_objects_v2",
        {},
        expected_params={"Bucket": "dessert-images", "Prefix": "homepage-display/"},
    )
    response = client.get("/display-images")
    pytest.helpers.assert_responses_equal(
        response, 404, {"detail": "No display images found"}
    )


def test_get_image_urls(s3_stub):
    s3_stub.add_response(
        "list_objects_v2",
        {
            "Contents": [
                {"Key": "homepage-display/image1.jpg"},
                {"Key": "homepage-display/image2.jpg"},
            ]
        },
        expected_params={"Bucket": "dessert-images", "Prefix": "homepage-display/"},
    )
    response = client.get("/display-images")
    pytest.helpers.assert_responses_equal(
        response,
        200,
        {},
        [
            "https://dessert-images.s3.amazonaws.com/display-images/image1.jpg",
            "https://dessert-images.s3.amazonaws.com/display-images/image2.jpg",
        ],
    )
