import pytest
from botocore.stub import Stubber
from fastapi import Form
from fastapi.testclient import TestClient

from src.api import app
from src.routes.post_forgot_password import cognito_client

test_client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("COGNITO_APP_CLIENT_ID", "123456789")


@pytest.fixture(autouse=True, scope="function")
def cognito_stub():
    with Stubber(cognito_client) as cognito_stubber:
        yield cognito_stubber
        cognito_stubber.assert_no_pending_responses()


def test_handler_valid_event_forgot_password(cognito_stub):
    cognito_stub.add_response(
        "forgot_password",
        {},
        expected_params={
            "ClientId": "123456789",
            "Username": "johndoe@gmail.com",
        },
    )

    response = test_client.post("/forgot_password", data={"email": "johndoe@gmail.com"})

    pytest.helpers.assert_responses_equal(
        response, 200, {"message": "Password reset email sent to johndoe@gmail.com"}
    )


def test_handler_invalid_username(cognito_stub):
    cognito_stub.add_client_error(
        "forgot_password",
        service_error_code="InvalidParameterException",
        expected_params={
            "ClientId": "123456789",
            "Username": "johndoe@gmail.com",
        },
    )

    response = test_client.post("/forgot_password", data={"email": "johndoe@gmail.com"})

    pytest.helpers.assert_responses_equal(
        response, 200, {"message": "Password reset email sent to johndoe@gmail.com"}
    )


def test_handler_client_error(cognito_stub):
    cognito_stub.add_client_error(
        "forgot_password",
        service_error_code="InternalErrorException",
        expected_params={"ClientId": "123456789", "Username": "johndoe@gmail.com"},
    )

    response = test_client.post("/forgot_password", data={"email": "johndoe@gmail.com"})

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {
            "detail": "An error occurred (InternalErrorException) when calling the ForgotPassword operation: "
        },
    )
