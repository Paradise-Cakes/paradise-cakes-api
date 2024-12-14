import pytest

from src.customize_emails_trigger.handler import lambda_handler
from tests.support import default_context


def test_lambda_handler():
    result = lambda_handler(
        {
            "response": {
                "autoConfirmUser": False,
                "autoVerifyEmail": False,
            }
        },
        default_context,
    )
    assert result == {
        "response": {
            "autoConfirmUser": True,
            "autoVerifyEmail": True,
        }
    }
