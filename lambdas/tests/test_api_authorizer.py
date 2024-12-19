from unittest.mock import patch

import pytest

from src.api_authorizer.handler import lambda_handler
from tests.support import default_context


def test_handler_grants_guests_access():
    event = {
        "methodArn": "arn:aws:execute-api:eu-west-1:123456789012:api-id/stage/GET/resource",
    }

    response = lambda_handler(event, default_context)

    assert response == {
        "principalId": "Unknown",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": "arn:aws:execute-api:eu-west-1:123456789012:api-id/stage/GET/resource",
                }
            ],
        },
        "context": {"user_email": None, "user_groups": ["guests"]},
    }


@patch("src.api_authorizer.handler.jwt")
def test_handler_grants_users_access(jwt_mock):
    jwt_mock.decode.return_value = {
        "email": "anthony.soprano@gmail.com",
        "cognito:groups": ["users"],
    }

    event = {
        "authorizationToken": "Bearer token",
        "methodArn": "arn:aws:execute-api:eu-west-1:123456789012:api-id/stage/GET/resource",
    }

    response = lambda_handler(event, default_context)

    assert response == {
        "principalId": "anthony.soprano@gmail.com",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": "arn:aws:execute-api:eu-west-1:123456789012:api-id/stage/GET/resource",
                }
            ],
        },
        "context": {
            "user_email": "anthony.soprano@gmail.com",
            "user_groups": ["users"],
        },
    }


@patch("src.api_authorizer.handler.jwt")
def test_handler_exception_denies_access(jwt_mock):
    jwt_mock.decode.side_effect = Exception("Invalid token")

    event = {
        "methodArn": "arn:aws:execute-api:eu-west-1:123456789012:api-id/stage/GET/resource",
        "authorizationToken": "Bearer invalid-token",
    }
    response = lambda_handler(event, default_context)

    assert response == {
        "principalId": "Unknown",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Deny",
                    "Resource": "arn:aws:execute-api:eu-west-1:123456789012:api-id/stage/GET/resource",
                }
            ],
        },
        "context": {"user_email": None, "user_groups": []},
    }
