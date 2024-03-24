import pytest
from fastapi import Form
from fastapi.testclient import TestClient
from src.api import app
from src.routes.post_signin import cognito_client
from botocore.stub import Stubber

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


def test_handler_valid_event_signin(cognito_stub):
    cognito_stub.add_response(
        "initiate_auth",
        {
            "ChallengeName": "PASSWORD_VERIFIER",
            "Session": "my-session-super-secret",
            "ChallengeParameters": {},
            "AuthenticationResult": {
                "AccessToken": "my-super-secret-token",
                "ExpiresIn": 3600,
                "TokenType": "Bearer",
                "RefreshToken": "my-super-secret-refresh-token",
                "IdToken": "my-super-secret-id-token",
                "NewDeviceMetadata": {
                    "DeviceKey": "my-device",
                    "DeviceGroupKey": "my-device-group",
                },
            },
        },
        expected_params={
            "AuthFlow": "USER_PASSWORD_AUTH",
            "AuthParameters": {
                "USERNAME": "anthony.viera@gmail.com",
                "PASSWORD": "password",
            },
            "ClientId": "123456789",
        },
    )

    response = test_client.post(
        "/signin",
        data={"email": "anthony.viera@gmail.com", "password": "password"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        200,
        {
            "ChallengeName": "PASSWORD_VERIFIER",
            "Session": "my-session-super-secret",
            "ChallengeParameters": {},
            "AuthenticationResult": {
                "AccessToken": "my-super-secret-token",
                "ExpiresIn": 3600,
                "TokenType": "Bearer",
                "RefreshToken": "my-super-secret-refresh-token",
                "IdToken": "my-super-secret-id-token",
                "NewDeviceMetadata": {
                    "DeviceKey": "my-device",
                    "DeviceGroupKey": "my-device-group",
                },
            },
        },
    )


def test_handler_invalid_event_signin_user_not_found(cognito_stub):
    cognito_stub.add_client_error(
        "initiate_auth",
        service_error_code="UserNotFoundException",
        expected_params={
            "AuthFlow": "USER_PASSWORD_AUTH",
            "AuthParameters": {
                "USERNAME": "anthony.viera@gmail.com",
                "PASSWORD": "password",
            },
            "ClientId": "123456789",
        },
    )

    request = test_client.post(
        "/signin",
        data={"email": "anthony.viera@gmail.com", "password": "password"},
    )

    pytest.helpers.assert_responses_equal(
        request,
        400,
        {"detail": "User not found with email"},
    )


def test_handler_invalid_event_signin_incorrect_password(cognito_stub):
    cognito_stub.add_client_error(
        "initiate_auth",
        service_error_code="NotAuthorizedException",
        expected_params={
            "AuthFlow": "USER_PASSWORD_AUTH",
            "AuthParameters": {
                "USERNAME": "anthony.viera@gmail.com",
                "PASSWORD": "password",
            },
            "ClientId": "123456789",
        },
    )

    response = test_client.post(
        "/signin",
        data={"email": "anthony.viera@gmail.com", "password": "password"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {"detail": "Incorrect password"},
    )


def test_handler_invalid_event_signin_client_error(cognito_stub):
    cognito_stub.add_client_error(
        "initiate_auth",
        service_error_code="InternalErrorException",
        expected_params={
            "AuthFlow": "USER_PASSWORD_AUTH",
            "AuthParameters": {
                "USERNAME": "anthony.viera@gmail.com",
                "PASSWORD": "password",
            },
            "ClientId": "123456789",
        },
    )

    response = test_client.post(
        "/signin",
        data={"email": "anthony.viera@gmail.com", "password": "password"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {"detail": "Something went wrong! :("},
    )
