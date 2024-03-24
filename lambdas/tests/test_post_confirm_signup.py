import pytest
from fastapi import Form
from fastapi.testclient import TestClient
from src.api import app
from src.routes.post_confirm_signup import cognito_client
from botocore.stub import Stubber

test_client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("COGNITO_APP_CLIENT_ID", "123456789")


@pytest.fixture(autouse=True, scope="function")
def cognito_stub():
    with Stubber(cognito_client) as cognito_stubber:
        yield cognito_stubber
        cognito_stubber.assert_no_pending_responses()


def test_handler_valid_event_confirm_signup(cognito_stub):
    cognito_stub.add_response(
        "confirm_sign_up",
        {},
        expected_params={
            "ClientId": "123456789",
            "Username": "anthony.viera@gmail.com",
            "ConfirmationCode": "123456",
        },
    )

    response = test_client.post(
        "/confirm_signup",
        data={"email": "anthony.viera@gmail.com", "confirmation_code": "123456"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        200,
        {"message": "User confirmed"},
    )


def test_handler_invalid_confirmation_code(cognito_stub):
    cognito_stub.add_client_error(
        "confirm_sign_up",
        service_error_code="CodeMismatchException",
        expected_params={
            "ClientId": "123456789",
            "Username": "anthony.viera@gmail.com",
            "ConfirmationCode": "123456",
        },
    )

    response = test_client.post(
        "/confirm_signup",
        data={"email": "anthony.viera@gmail.com", "confirmation_code": "123456"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {"detail": "Invalid confirmation code"},
    )


def test_handler_expired_confirmation_code(cognito_stub):
    cognito_stub.add_client_error(
        "confirm_sign_up",
        service_error_code="ExpiredCodeException",
        expected_params={
            "ClientId": "123456789",
            "Username": "anthony.viera@gmail.com",
            "ConfirmationCode": "123456",
        },
    )

    response = test_client.post(
        "/confirm_signup",
        data={"email": "anthony.viera@gmail.com", "confirmation_code": "123456"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {"detail": "Confirmation code expired"},
    )


def test_handler_client_error(cognito_stub):
    cognito_stub.add_client_error(
        "confirm_sign_up",
        service_error_code="InternalErrorException",
        expected_params={
            "ClientId": "123456789",
            "Username": "anthony.viera@gmail.com",
            "ConfirmationCode": "123456",
        },
    )

    response = test_client.post(
        "/confirm_signup",
        data={"email": "anthony.viera@gmail.com", "confirmation_code": "123456"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {
            "detail": "An error occurred (InternalErrorException) when calling the ConfirmSignUp operation: "
        },
    )
