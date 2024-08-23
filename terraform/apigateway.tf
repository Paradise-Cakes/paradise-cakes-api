module "api_gateway" {
  source = "git@github.com:Paradise-Cakes/pc-terraform-modules.git//apiGateway?ref=v1.1.0"

  api_gateway_name                              = "paradise-cakes-api-gateway"
  api_description                               = "Proxy to handle requests to paradise cakes API"
  binary_media_types                            = ["multipart/form-data"]
  stage_name                                    = "v1"
  certificate_arn                               = aws_acm_certificate.paradise_cakes.arn
  acm_certificate_api_domain_validation_options = aws_acm_certificate.paradise_cakes.domain_validation_options
  api_domain_name                               = aws_acm_certificate.paradise_cakes.domain_name
  lambda_function_arn                           = aws_lambda_function.app.invoke_arn
  environment                                   = var.environment
  api_zone_id                                   = data.aws_route53_zone.paradise_cakes_api.zone_id
  prod_api_name                                 = "api.paradisecakesbymegan.com"
  dev_api_name                                  = "dev-api.paradisecakesbymegan.com"
  website_zone_id                               = data.aws_route53_zone.paradise_cakes[0].zone_id
  prod_api_name_servers                         = data.aws_route53_zone.paradise_cakes_api.name_servers
  dev_api_name_servers                          = ["ns-510.awsdns-63.com", "ns-1870.awsdns-41.co.uk", "ns-647.awsdns-16.net", "ns-1266.awsdns-30.org"]


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
