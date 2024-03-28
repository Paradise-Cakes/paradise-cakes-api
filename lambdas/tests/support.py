from aws_lambda_context import LambdaContext

default_context = LambdaContext()
default_context.function_name = "test"
default_context.memory_limit_in_mb = 256
default_context.invoked_function_arn = "arn:unit:::test/tests"
default_context.aws_request_id = "12345"
