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
}

resource "aws_lambda_permission" "allow_api_gateway_handler" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.app.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.paradise_cakes_api.execution_arn}/*"
}
