import pytest
from fastapi import Form
from fastapi.testclient import TestClient
from src.api import app
from src.routes.post_resend_confirmation_code import cognito_client
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


def test_handler_valid_event_resend_confirmation_code(cognito_stub):
    cognito_stub.add_response(
        "resend_confirmation_code",
        {},
        expected_params={
            "ClientId": "123456789",
            "Username": "anthony.viera@gmail.com",
        },
    )

    response = test_client.post(
        "/resend_confirmation_code",
        data={"email": "anthony.viera@gmail.com"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        200,
        {"message": "Confirmation code resent"},
    )


def test_handler_user_not_found(cognito_stub):
    cognito_stub.add_client_error(
        "resend_confirmation_code",
        service_error_code="UserNotFoundException",
        expected_params={
            "ClientId": "123456789",
            "Username": "anthony.viera@gmail.com",
        },
    )

    response = test_client.post(
        "/resend_confirmation_code",
        data={"email": "anthony.viera@gmail.com"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {"detail": "User not found"},
    )


def test_handler_limit_exceeded(cognito_stub):
    cognito_stub.add_client_error(
        "resend_confirmation_code",
        service_error_code="LimitExceededException",
        expected_params={
            "ClientId": "123456789",
            "Username": "anthony.viera@gmail.com",
        },
    )

    response = test_client.post(
        "/resend_confirmation_code",
        data={"email": "anthony.viera@gmail.com"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {"detail": "Limit exceeded, please try again later"},
    )


def test_handler_invalid_password(cognito_stub):
    cognito_stub.add_client_error(
        "resend_confirmation_code",
        service_error_code="NotAuthorizedException",
        expected_params={
            "ClientId": "123456789",
            "Username": "anthony.viera@gmail.com",
        },
    )

    response = test_client.post(
        "/resend_confirmation_code",
        data={"email": "anthony.viera@gmail.com"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {"detail": "Invalid password"},
    )


def test_handler_client_error(cognito_stub):
    cognito_stub.add_client_error(
        "resend_confirmation_code",
        service_error_code="InternalErrorException",
        expected_params={
            "ClientId": "123456789",
            "Username": "anthony.viera@gmail.com",
        },
    )

    response = test_client.post(
        "/resend_confirmation_code", data={"email": "anthony.viera@gmail.com"}
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {
            "detail": "An error occurred (InternalErrorException) when calling the ResendConfirmationCode operation: "
        },
    )
