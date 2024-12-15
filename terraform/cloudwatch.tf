resource "aws_cloudwatch_log_group" "app" {
  name              = "/aws/lambda/paradise-cakes-api-us-east-1"
  retention_in_days = 3
}

resource "aws_cloudwatch_log_group" "customize_emails_trigger" {
  name              = "/aws/lambda/customize-emails-trigger"
  retention_in_days = 3
}
