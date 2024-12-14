from aws_lambda_powertools import Logger

logger = Logger()


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    return {
        "message": "Hello from customize_emails_trigger!",
    }
