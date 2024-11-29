module "api_gateway" {
  source = "git@github.com:Paradise-Cakes/pc-terraform-modules.git//apiGateway?ref=v1.1.2"

  app_arn                                       = aws_lambda_function.app.arn
  api_gateway_name                              = "paradise-cakes-api-gateway"
  api_description                               = "Proxy to handle requests to paradise cakes API"
  binary_media_types                            = ["multipart/form-data"]
  stage_name                                    = "v1"
  api_acm_certificate_arn                       = aws_acm_certificate.paradise_cakes.arn
  acm_certificate_api_domain_validation_options = aws_acm_certificate.paradise_cakes.domain_validation_options
  api_domain_name                               = aws_acm_certificate.paradise_cakes.domain_name
  lambda_function_arn                           = aws_lambda_function.app.invoke_arn
  environment                                   = var.environment
  api_zone_id                                   = data.aws_route53_zone.paradise_cakes_api.zone_id
  prod_api_name                                 = "api.megsparadisecakes.com"  
  dev_api_name                                  = "dev-api.megsparadisecakes.com"    
  primary_hosted_zone_id                        = "Z07149123H5T9UU1DMO2K"
  # prod_api_name_servers                         = ["ns-1937.awsdns-50.co.uk", "ns-1013.awsdns-62.net", "ns-1115.awsdns-11.org", "ns-362.awsdns-45.com"]
  # dev_api_name_servers                          = ["ns-510.awsdns-63.com", "ns-1870.awsdns-41.co.uk", "ns-647.awsdns-16.net", "ns-1266.awsdns-30.org"]


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
