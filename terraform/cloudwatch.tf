data "aws_cloudwatch_log_group" "app" {
  name              = "/aws/lambda/${aws_lambda_function.app.function_name}"
  retention_in_days = 3
}

data "aws_cloudwatch_log_group" "customize_emails_trigger" {
  name              = "/aws/lambda/${aws_lambda_function.customize_emails_trigger.function_name}"
  retention_in_days = 3
}