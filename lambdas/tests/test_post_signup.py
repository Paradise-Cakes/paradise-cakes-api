import pytest
from botocore.stub import Stubber
from fastapi import Form
from fastapi.testclient import TestClient

from src.api import app
from src.routes.post_signup import cognito_client

test_client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("USER_POOL_ID", "us-east-1_123456789")
    monkeypatch.setenv("COGNITO_APP_CLIENT_ID", "123456789")


@pytest.fixture(autouse=True, scope="function")
def cognito_stub():
    with Stubber(cognito_client) as cognito_stubber:
        yield cognito_stubber
        cognito_stubber.assert_no_pending_responses()


def test_handler_valid_event_signup(cognito_stub):
    cognito_stub.add_response(
        "sign_up",
        {
            "UserConfirmed": True,
            "UserSub": "123456789",
        },
        expected_params={
            "ClientId": "123456789",
            "Username": "anthony.viera@gmail.com",
            "Password": "password",
            "UserAttributes": [
                {"Name": "email", "Value": "anthony.viera@gmail.com"},
                {"Name": "given_name", "Value": "Anthony"},
                {"Name": "family_name", "Value": "Viera"},
            ],
        },
    )

    response = test_client.post(
        "/signup",
        data={
            "email": "anthony.viera@gmail.com",
            "password": "password",
            "first_name": "Anthony",
            "last_name": "Viera",
        },
    )
    pytest.helpers.assert_responses_equal(
        response,
        201,
        {
            "message": "User created",
            "UserConfirmed": True,
            "UserSub": "123456789",
            "email": "anthony.viera@gmail.com",
            "given_name": "Anthony",
            "family_name": "Viera",
        },
    )


def test_handler_invalid_event_signup_username_exists(cognito_stub):
    cognito_stub.add_client_error(
        "sign_up",
        service_error_code="UsernameExistsException",
        expected_params={
            "ClientId": "123456789",
            "Username": "anthony.viera@gmail.com",
            "Password": "password",
            "UserAttributes": [
                {"Name": "email", "Value": "anthony.viera@gmail.com"},
                {"Name": "given_name", "Value": "Anthony"},
                {"Name": "family_name", "Value": "Viera"},
            ],
        },
    )

    response = test_client.post(
        "/signup",
        data={
            "email": "anthony.viera@gmail.com",
            "password": "password",
            "first_name": "Anthony",
            "last_name": "Viera",
        },
    )

    pytest.helpers.assert_responses_equal(
        response, 400, {"detail": "User already exists with that email"}
    )


def test_handler_invalid_event_signup_password_too_easy(cognito_stub):
    cognito_stub.add_client_error(
        "sign_up",
        service_error_code="InvalidPasswordException",
        expected_params={
            "ClientId": "123456789",
            "Username": "anthony.viera@gmail.com",
            "Password": "password",
            "UserAttributes": [
                {"Name": "email", "Value": "anthony.viera@gmail.com"},
                {"Name": "given_name", "Value": "Anthony"},
                {"Name": "family_name", "Value": "Viera"},
            ],
        },
    )

    response = test_client.post(
        "/signup",
        data={
            "email": "anthony.viera@gmail.com",
            "password": "password",
            "first_name": "Anthony",
            "last_name": "Viera",
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {
            "detail": "Password must have uppercase, lowercase, number, special character, and be at least 8 characters long"
        },
    )


def test_handler_invalid_event_signup_client_error(cognito_stub):
    cognito_stub.add_client_error(
        "sign_up",
        service_error_code="InternalErrorException",
        expected_params={
            "ClientId": "123456789",
            "Username": "anthony.viera@gmail.com",
            "Password": "password",
            "UserAttributes": [
                {"Name": "email", "Value": "anthony.viera@gmail.com"},
                {"Name": "given_name", "Value": "Anthony"},
                {"Name": "family_name", "Value": "Viera"},
            ],
        },
    )

    response = test_client.post(
        "/signup",
        data={
            "email": "anthony.viera@gmail.com",
            "password": "password",
            "first_name": "Anthony",
            "last_name": "Viera",
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {
            "detail": "An error occurred (InternalErrorException) when calling the SignUp operation: "
        },
    )
