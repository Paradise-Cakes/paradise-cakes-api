resource "aws_lambda_function" "app" {
  image_uri     = "${aws_ecr_repository.paradise_cakes_api_lambda.repository_url}:${var.docker_image_tag}"
  package_type  = "Image"
  function_name = "paradise-cakes-api-us-east-1"
  role          = aws_iam_role.paradise_cakes_api_role.arn

  timeout     = 30
  memory_size = 1024

  image_config {
    command = ["handler.handler"]
  }
}