from aws_lambda_powertools import Logger

logger = Logger()


def lambda_handler(event, context):
    # Extract the token from the Authorization header
    token = event.get("authorizationToken", "")

    # Validate the token (replace with real validation logic)
    if token == "Bearer valid-token":
        return generate_policy("user", "Allow", event["methodArn"])
    else:
        return generate_policy("user", "Deny", event["methodArn"])


def generate_policy(principal_id, effect, resource):
    policy = {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {"Action": "execute-api:Invoke", "Effect": effect, "Resource": resource}
            ],
        },
    }
    return policy
