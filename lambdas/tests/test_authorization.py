import pytest
from unittest.mock import patch, Mock
from fastapi import HTTPException, Request
from jose import JWTError
import requests
from src.lib.authorization import get_jwks, verify_cognito_token, admin_only
import pytest
from unittest.mock import patch
from fastapi import HTTPException
from jose import JWTError
from src.lib.authorization import get_jwks, verify_cognito_token, admin_only


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("REGION", "us-east-1")
    monkeypatch.setenv("COGNITO_USER_POOL_ID", "test_user_pool_id")
    monkeypatch.setenv("COGNITO_APP_CLIENT_ID", "test_app_client_id")


def create_request_with_cookie(token: str):
    request = Request(
        scope={
            "type": "http",
            "headers": [],
        }
    )
    request._cookies = {"access_token": token}  # Simulating having a cookie
    return request


def test_get_jwks_success(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"keys": []}
    mocker.patch("requests.get", return_value=mock_response)
    assert get_jwks() == {"keys": []}


def test_get_jwks_failure(mocker):
    mocker.patch("requests.get", side_effect=requests.RequestException)
    with pytest.raises(HTTPException):
        get_jwks()


def test_verify_cognito_token_success(mocker):
    mocker.patch(
        "src.lib.authorization.get_jwks",
        return_value={
            "keys": [
                {
                    "kid": "test_kid",
                    "kty": "RS256",
                    "use": "sig",
                    "n": "test_n",
                    "e": "test_e",
                }
            ]
        },
    )
    mocker.patch(
        "src.lib.authorization.jwt.get_unverified_headers",
        return_value={"kid": "test_kid"},
    )
    mocker.patch(
        "src.lib.authorization.jwt.decode", return_value={"payload": "test_payload"}
    )
    assert verify_cognito_token(create_request_with_cookie("test_token")) == {
        "payload": "test_payload"
    }


def test_verify_cognito_token_jwt_error(mocker):
    mocker.patch(
        "src.lib.authorization.get_jwks",
        return_value={
            "keys": [
                {
                    "kid": "test_kid",
                    "kty": "RS256",
                    "use": "sig",
                    "n": "test_n",
                    "e": "test_e",
                }
            ]
        },
    )
    mocker.patch(
        "src.lib.authorization.jwt.get_unverified_headers",
        return_value={"kid": "test_kid"},
    )
    mocker.patch("src.lib.authorization.jwt.decode", side_effect=JWTError)
    with pytest.raises(HTTPException):
        verify_cognito_token(create_request_with_cookie("test_token"))


def test_verify_cognito_token_no_matching_kid(mocker):
    mocker.patch(
        "src.lib.authorization.get_jwks",
        return_value={
            "keys": [
                {
                    "kid": "test_kid",
                    "kty": "RS256",
                    "use": "sig",
                    "n": "test_n",
                    "e": "test_e",
                }
            ]
        },
    )
    mocker.patch(
        "src.lib.authorization.jwt.get_unverified_headers",
        return_value={"kid": "wrong_kid"},
    )
    with pytest.raises(HTTPException):
        with pytest.raises(JWTError):
            verify_cognito_token(create_request_with_cookie("test_token"))


def test_admin_only_success(mocker):
    mocker.patch(
        "src.lib.authorization.verify_cognito_token",
        return_value={"cognito:groups": ["paradise-cakes-admin-group"]},
    )
    assert admin_only(create_request_with_cookie("test_token")) is None


def test_admin_only_failure(mocker):
    mocker.patch(
        "src.lib.authorization.verify_cognito_token",
        return_value={"cognito:groups": ["users"]},
    )
    with pytest.raises(HTTPException) as e:
        admin_only(create_request_with_cookie("test_token"))
    assert str(e.value) == "404: Not found"
