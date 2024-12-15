import pytest

from src.customize_emails_trigger.handler import lambda_handler
from tests.support import default_context


def test_handler_confirm_signup_message():
    event = {
        "request": {
            "userAttributes": {"given_name": "Anthony"},
            "codeParameter": "123456",
        },
        "triggerSource": "CustomMessage_SignUp",
        "response": {
            "emailSubject": "Why hello there!",
            "emailMessage": "This is a test message",
        },
    }
    result = lambda_handler(event, default_context)
    assert result["response"]["emailSubject"] == "Welcome to Paradise Cakes!"
    assert result["response"]["emailMessage"] == (
        "Hi Anthony,<br><br>"
        "Thank you for signing up for Paradise Cakes! "
        "Your verification code is: <b>123456</b><br><br>"
        "Use this code to complete your registration."
    )


def test_handler_forgot_password_message():
    event = {
        "request": {
            "userAttributes": {"given_name": "Anthony"},
            "codeParameter": "123456",
        },
        "triggerSource": "CustomMessage_ForgotPassword",
        "response": {
            "emailSubject": "Why hello there!",
            "emailMessage": "This is a test message",
        },
    }
    result = lambda_handler(event, default_context)
    assert result["response"]["emailSubject"] == "Reset Your Password"
    assert result["response"]["emailMessage"] == (
        "Hello Anthony,<br><br>"
        "We received a request to reset your password. Your reset code is: "
        f"<b>123456</b><br><br>"
        "If you did not request this, please ignore this email."
    )
