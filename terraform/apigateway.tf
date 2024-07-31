resource "aws_api_gateway_rest_api" "paradise_cakes_api" {
  name        = "paradise-cakes-api-gateway"
  description = "Proxy to handle requests to paradise cakes API"

  binary_media_types = [
    "multipart/form-data"
  ]
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.paradise_cakes_api.id
  parent_id   = aws_api_gateway_rest_api.paradise_cakes_api.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "paradise_cakes_proxy" {
  rest_api_id   = aws_api_gateway_rest_api.paradise_cakes_api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_stage" "paradise_cakes" {
  stage_name           = "v1"
  rest_api_id          = aws_api_gateway_rest_api.paradise_cakes_api.id
  deployment_id        = aws_api_gateway_deployment.paradise_cakes_api.id
  xray_tracing_enabled = true
  cache_cluster_size   = "0.5"
}

resource "aws_api_gateway_deployment" "paradise_cakes_api" {
  rest_api_id = aws_api_gateway_rest_api.paradise_cakes_api.id
  depends_on = [
    aws_api_gateway_integration.paradise_cakes_integration,
    aws_api_gateway_integration.cors
  ]

  triggers = {
    redeployment = timestamp()
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_domain_name" "api" {
  count           = var.environment == "prod" ? 1 : 0
  certificate_arn = aws_acm_certificate.paradise_cakes[0].arn
  domain_name     = aws_acm_certificate.paradise_cakes[0].domain_name
}

resource "aws_api_gateway_base_path_mapping" "path_mapping_internal" {
  count       = var.environment == "prod" ? 1 : 0
  api_id      = aws_api_gateway_rest_api.paradise_cakes_api.id
  stage_name  = aws_api_gateway_stage.paradise_cakes.stage_name
  domain_name = aws_api_gateway_domain_name.api[0].domain_name
  base_path   = aws_api_gateway_stage.paradise_cakes.stage_name
}

resource "aws_api_gateway_domain_name" "api_dev" {
  count           = var.environment == "prod" ? 0 : 1
  certificate_arn = data.aws_acm_certificate.paradise_cakes_dev[0].arn
  domain_name     = data.aws_acm_certificate.paradise_cakes_dev[0].domain_name
}

resource "aws_api_gateway_base_path_mapping" "path_mapping_internal_dev" {
  count       = var.environment == "prod" ? 0 : 1
  api_id      = aws_api_gateway_rest_api.paradise_cakes_api.id
  stage_name  = aws_api_gateway_stage.paradise_cakes.stage_name
  domain_name = aws_api_gateway_domain_name.api_dev[0].domain_name
  base_path   = aws_api_gateway_stage.paradise_cakes.stage_name
}

resource "aws_api_gateway_integration" "paradise_cakes_integration" {
  rest_api_id             = aws_api_gateway_rest_api.paradise_cakes_api.id
  resource_id             = aws_api_gateway_resource.proxy.id
  http_method             = aws_api_gateway_method.paradise_cakes_proxy.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.app.invoke_arn
}

resource "aws_api_gateway_rest_api_policy" "paradise_cakes_api" {
  rest_api_id = aws_api_gateway_rest_api.paradise_cakes_api.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "execute-api:Invoke",
      "Resource": ["execute-api:/*/*/*"]
    }
  ]
}
EOF
}


resource "aws_api_gateway_method" "cors" {
  rest_api_id   = aws_api_gateway_rest_api.paradise_cakes_api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "cors" {
  rest_api_id = aws_api_gateway_rest_api.paradise_cakes_api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.cors.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = <<EOF
{
  "statusCode": 200
}
EOF
  }
}

resource "aws_api_gateway_method_response" "cors" {
  rest_api_id = aws_api_gateway_rest_api.paradise_cakes_api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.cors.http_method
  status_code = 200

  response_models = {
    "application/json" = "Empty"
  }

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "cors" {
  rest_api_id = aws_api_gateway_rest_api.paradise_cakes_api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.cors.http_method
  status_code = 200

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization,User-Agent'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS,GET,PUT,DELETE,PATCH'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

