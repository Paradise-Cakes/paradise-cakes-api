provider "aws" {
  region = "us-east-1"
}

data "aws_route53_zone" "paradise_cakes" {
  count = var.environment == "prod" ? 1 : 0
  name  = "paradisecakesbymegan.com"
}

resource "aws_route53_record" "api_record" {
  count   = var.environment == "prod" ? 1 : 0
  zone_id = data.aws_route53_zone.paradise_cakes[0].zone_id
  name    = "api.paradisecakesbymegan.com"
  type    = "A"

  alias {
    name                   = aws_api_gateway_domain_name.api.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.api.cloudfront_zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "api_record_dev" {
  count   = var.environment == "prod" ? 1 : 0
  zone_id = data.aws_route53_zone.paradise_cakes[0].zone_id
  name    = "dev-api.paradisecakesbymegan.com"
  type    = "A"

  alias {
    name                   = aws_api_gateway_domain_name.api.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.api.cloudfront_zone_id
    evaluate_target_health = true
  }
}
