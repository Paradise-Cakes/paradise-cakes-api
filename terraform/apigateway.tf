resource "aws_api_gateway_rest_api" "paradise_cakes_api" {
  name        = "paradise-cakes-api-gateway"
  description = "Proxy to handle requests to paradise cakes API"
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
  depends_on  = [aws_api_gateway_integration.paradise_cakes_integration]

  triggers = {
    redeployment = timestamp()
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_domain_name" "paradise_cakes_cloud" {
  certificate_arn = aws_acm_certificate.paradise_cakes_cloud.arn
  domain_name     = aws_acm_certificate.paradise_cakes_cloud.domain_name
}

resource "aws_api_gateway_base_path_mapping" "path_mapping_internal" {
  api_id      = aws_api_gateway_rest_api.paradise_cakes_api.id
  stage_name  = aws_api_gateway_stage.paradise_cakes.stage_name
  domain_name = aws_api_gateway_domain_name.paradise_cakes_cloud.domain_name
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


resource "aws_api_gateway_authorizer" "paradise_cakes_authorizer" {
  name            = "paradise-cakes-authorizer"
  rest_api_id     = aws_api_gateway_rest_api.paradise_cakes_api.id
  type            = "COGNITO_USER_POOLS"
  provider_arns   = [aws_cognito_user_pool.paradise_cakes_user_pool.arn]
  identity_source = "method.request.header.Authorization"
}


