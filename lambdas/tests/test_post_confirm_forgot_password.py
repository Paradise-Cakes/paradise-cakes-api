import pytest
from botocore.stub import Stubber
from fastapi.testclient import TestClient

from src.api import app
from src.routes.post_confirm_forgot_password import cognito_client

test_client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("COGNITO_APP_CLIENT_ID", "123456789")


@pytest.fixture(autouse=True, scope="function")
def cognito_stub():
    with Stubber(cognito_client) as cognito_stubber:
        yield cognito_stubber
        cognito_stubber.assert_no_pending_responses()


def test_handler_valid_event_confirm_forgot_password(cognito_stub):
    cognito_stub.add_response(
        "confirm_forgot_password",
        {},
        expected_params={
            "ClientId": "123456789",
            "Username": "anthony.soprano@gmail.com",
            "ConfirmationCode": "123",
            "Password": "3r@fv3sagv#",
        },
    )

    response = test_client.post(
        "/confirm_forgot_password",
        data={
            "email": "anthony.soprano@gmail.com",
            "code": "123",
            "password": "3r@fv3sagv#",
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        200,
        {"message": "Password reset for anthony.soprano@gmail.com successful"},
    )


def test_handler_invalid_request(cognito_stub):
    cognito_stub.add_client_error(
        "confirm_forgot_password",
        service_error_code="InvalidParameterException",
        expected_params={
            "ClientId": "123456789",
            "Username": "anthony.soprano@gmail.com",
            "ConfirmationCode": "123",
            "Password": "thisIsMyNewPassword123@",
        },
        service_message="OH NO!!!!",
    )

    response = test_client.post(
        "/confirm_forgot_password",
        data={
            "email": "anthony.soprano@gmail.com",
            "code": "123",
            "password": "thisIsMyNewPassword123@",
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {
            "detail": "An error occurred (InvalidParameterException) when calling the ConfirmForgotPassword operation: OH NO!!!!"
        },
    )
