import pytest
from botocore.stub import Stubber
from fastapi.testclient import TestClient

from src.api import app
from src.routes.post_logout import cognito_client

test_client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("USER_POOL_ID", "us-east-1_123456789")


@pytest.fixture(autouse=True, scope="function")
def cognito_stub():
    with Stubber(cognito_client) as cognito_stubber:
        yield cognito_stubber
        cognito_stubber.assert_no_pending_responses()


def test_handler_valid_event_logout(cognito_stub):
    cognito_stub.add_response(
        "global_sign_out",
        {},
        expected_params={
            "AccessToken": "my-super-secret-token",
        },
    )

    response = test_client.post(
        "/logout",
        cookies={"access_token": "my-super-secret-token"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        200,
        {"message": "User logged out successfully"},
    )


def test_handler_no_access_token():
    response = test_client.post(
        "/logout",
    )

    pytest.helpers.assert_responses_equal(
        response,
        200,
        {"message": "User logged out successfully"},
    )


def test_handler_invalid_access_token(cognito_stub):
    cognito_stub.add_client_error(
        "global_sign_out",
        service_error_code="NotAuthorizedException",
        expected_params={"AccessToken": "wut is this"},
    )

    response = test_client.post(
        "/logout",
        cookies={"access_token": "wut is this"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {
            "detail": "An error occurred (NotAuthorizedException) when calling the GlobalSignOut operation: "
        },
    )
