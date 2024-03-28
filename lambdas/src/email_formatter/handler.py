import boto3
import json
import os
import re
from aws_lambda_powertools import Logger


logger = Logger()


# @logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    logger.info("Received SNS email event")

    sns_message_string = event.get("Message")
    sns_message = json.loads(sns_message_string)
    content = sns_message.get("content")

    pattern = r"Content-Type: text/html; charset=\"UTF-8\"\r\n\r\n(.*?)\r\n\r\n--"

    match = re.search(pattern, content, re.DOTALL)

    if match:
        message_content = match.group(1)
        print(f"Here is the message content: {message_content}")
    else:
        print("No match found")
