import pytest

from src.api_authorizer.handler import lambda_handler
from tests.support import default_context


def test_lambda_handler():
    event = {
        "authorizationToken": "Bearer valid-token",
        "methodArn": "arn:aws:execute-api:us-east-1:123456789012:api-id/stage/GET/resource",
    }
    result = lambda_handler(event, default_context)
    assert result["principalId"] == "user"
    assert result["policyDocument"]["Statement"][0]["Effect"] == "Allow"


def test_lambda_handler_invalid_token():
    event = {
        "authorizationToken": "Bearer LET ME IN, LET ME INNNN",
        "methodArn": "arn:aws:execute-api:us-east-1:123456789012:api-id/stage/GET/resource",
    }
    result = lambda_handler(event, default_context)
    assert result["principalId"] == "user"
    assert result["policyDocument"]["Statement"][0]["Effect"] == "Deny"
