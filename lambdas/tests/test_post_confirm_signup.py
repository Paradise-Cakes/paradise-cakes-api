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

    cognito_stub.add_response(
        "get_user",
        {
            "Username": "anthony.viera@gmail.com",
            "UserAttributes": [
                {"Name": "email", "Value": "anthony.viera@gmail.com"},
                {"Name": "given_name", "Value": "Anthony"},
                {"Name": "family_name", "Value": "Viera"},
            ],
        },
    )

    response = test_client.post(
        "/confirm_signup",
        data={
            "email": "anthony.viera@gmail.com",
            "password": "password",
            "confirmation_code": "123456",
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        200,
        {
            "message": "User confirmed and signed in",
            "email": "anthony.viera@gmail.com",
            "given_name": "Anthony",
            "family_name": "Viera",
        },
    )


def test_handler_no_access_token(cognito_stub):
    cognito_stub.add_response(
        "confirm_sign_up",
        {},
        expected_params={
            "ClientId": "123456789",
            "Username": "anthony.viera@gmail.com",
            "ConfirmationCode": "123456",
        },
    )
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
    cognito_stub.add_client_error(
        "get_user",
        service_error_code="NotAuthorizedException",
        expected_params={"AccessToken": "my-super-secret-token"},
    )

    response = test_client.post(
        "/confirm_signup",
        data={
            "email": "anthony.viera@gmail.com",
            "password": "password",
            "confirmation_code": "123456",
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {
            "detail": "An error occurred (NotAuthorizedException) when calling the GetUser operation: "
        },
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
        data={
            "email": "anthony.viera@gmail.com",
            "password": "password",
            "confirmation_code": "123456",
        },
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
        data={
            "email": "anthony.viera@gmail.com",
            "password": "password",
            "confirmation_code": "123456",
        },
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
        data={
            "email": "anthony.viera@gmail.com",
            "password": "password",
            "confirmation_code": "123456",
        },
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {
            "detail": "An error occurred (InternalErrorException) when calling the ConfirmSignUp operation: "
        },
    )
