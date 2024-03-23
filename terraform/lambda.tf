resource "aws_lambda_function" "app" {
  image_uri     = "${aws_ecr_repository.paradise_cakes_api_lambda.repository_url}:${var.docker_image_tag}"
  package_type  = "Image"
  function_name = "paradise-cakes-api-us-east-1"
  role          = aws_iam_role.lambda_execution_role.arn

  timeout     = 30
  memory_size = 1024

  image_config {
    command = ["src.api.lambda_handler"]
  }

  environment {
    variables = {
      DYNAMODB_REGION = "us-east-1"
      DYNAMODB_ENDPOINT_URL = "https://dynamodb.us-east-1.amazonaws.com"
      DYNAMODB_DESSERTS_TABLE_NAME = aws_dynamodb_table.desserts.name
      DYNAMODB_ORDERS_TABLE_NAME = aws_dynamodb_table.orders.name
      CLIENT_ID = aws_cognito_user_pool_client.paradise_cakes_client.id
    }
  }
}

resource "aws_lambda_permission" "allow_api_gateway_handler" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.app.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.paradise_cakes_api.execution_arn}/*"
}
