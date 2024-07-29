resource "aws_route53_zone" "paradise_cakes" {
  name = var.environment == "prod" ? "api-paradisecakesbymegan.com" : "dev-api.paradisecakesbymegan.com"
}

resource "aws_route53_record" "api" {
  zone_id = aws_route53_zone.paradise_cakes.zone_id
  name    = var.environment == "prod" ? "api.paradisecakesbymegan.com" : "dev-api.paradisecakesbymegan.com"
  type    = "A"

  alias {
    name                   = aws_api_gateway_domain_name.paradise_cakes.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.paradise_cakes.cloudfront_zone_id
    evaluate_target_health = true
  }
}
