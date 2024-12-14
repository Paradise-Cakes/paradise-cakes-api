from aws_lambda_powertools import Logger

logger = Logger()


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    first_name = event.get("request").get("userAttributes").get("given_name")
    trigger_source = event.get("triggerSource")
    code = event.get("request").get("codeParameter")

    if trigger_source == "CustomMessage_SignUp":
        event["response"]["emailSubject"] = "Welcome to Paradise Cakes!"
        event["response"]["emailMessage"] = (
            f"Hi {first_name},<br><br>"
            "Thank you for signing up for Paradise Cakes! "
            f"Your verification code is: <b>{code}</b><br><br>"
            "Use this code to complete your registration."
        )

    elif trigger_source == "CustomMessage_ForgotPassword":
        event["response"]["emailSubject"] = "Reset Your Password"
        event["response"]["emailMessage"] = (
            f"Hello {first_name},<br><br>"
            "We received a request to reset your password. Your reset code is: "
            f"<b>{code}</b><br><br>"
            "If you did not request this, please ignore this email."
        )

    return event
