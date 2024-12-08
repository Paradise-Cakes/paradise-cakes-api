resource "aws_lambda_function" "app" {
  image_uri     = "${data.aws_ecr_repository.paradise_cakes_api_lambda.repository_url}:${var.docker_image_tag}"
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
      DYNAMODB_REGION                        = "us-east-1"
      DYNAMODB_ENDPOINT_URL                  = "https://dynamodb.us-east-1.amazonaws.com"
      DYNAMODB_DESSERTS_TABLE_NAME           = aws_dynamodb_table.desserts.name
      DYNAMODB_DESSERT_TYPE_COUNT_TABLE_NAME = aws_dynamodb_table.dessert_type_count.name
      DYNAMODB_ORDERS_TABLE_NAME             = aws_dynamodb_table.orders.name
      DYNAMODB_ORDER_TYPE_COUNT_TABLE_NAME   = aws_dynamodb_table.order_type_count.name
      DYNAMODB_PRICES_TABLE_NAME             = aws_dynamodb_table.prices.name
      COGNITO_APP_CLIENT_ID                  = aws_cognito_user_pool_client.paradise_cakes_client.id
      COGNITO_USER_POOL_ID                   = aws_cognito_user_pool.paradise_cakes_user_pool.id
      REGION                                 = "us-east-1"
      DESSERT_IMAGES_BUCKET_NAME             = aws_s3_bucket.pc_dessert_images_bucket.bucket
    }
  }
}
