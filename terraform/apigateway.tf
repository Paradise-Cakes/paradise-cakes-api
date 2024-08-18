module "api_gateway" {
  source = "git@github.com:Paradise-Cakes/pc-terraform-modules.git//apiGateway?ref=v1.0.0"

  api_name            = "paradise-cakes-api-gateway"
  api_description     = "Proxy to handle requests to paradise cakes API"
  binary_media_types  = ["multipart/form-data"]
  stage_name          = "v1"
  certificate_arn     = aws_acm_certificate.paradise_cakes.arn
  domain_name         = aws_acm_certificate.paradise_cakes.domain_name
  lambda_function_arn = aws_lambda_function.app.invoke_arn
  policy              = <<EOF
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
