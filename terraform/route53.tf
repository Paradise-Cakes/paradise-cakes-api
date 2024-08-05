data "aws_route53_zone" "paradise_cakes_api" {
  name = var.environment == "prod" ? "api.paradisecakesbymegan.com" : "dev-api.paradisecakesbymegan.com"
}

resource "aws_route53_record" "api_record" {
  zone_id = data.aws_route53_zone.paradise_cakes_api.zone_id
  name    = var.environment == "prod" ? "api.paradisecakesbymegan.com" : "dev-api.paradisecakesbymegan.com"
  type    = "A"

  alias {
    name                   = aws_api_gateway_domain_name.api.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.api.cloudfront_zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "paradise_cakes_validation_record" {
  for_each = {
    for dvo in aws_acm_certificate.paradise_cakes.domain_validation_options : dvo.domain_name => {
      name    = dvo.resource_record_name
      record  = dvo.resource_record_value
      type    = dvo.resource_record_type
      zone_id = data.aws_route53_zone.paradise_cakes_api.zone_id
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = each.value.zone_id

  depends_on = [aws_route53_record.paradise_cakes_api_ns]
}

data "aws_route53_zone" "paradise_cakes" {
  name         = var.environment == "prod" ? "paradisecakesbymegan.com" : "dev.paradisecakesbymegan.com"
  private_zone = false
}

resource "aws_route53_record" "paradise_cakes_api_ns" {
  zone_id = data.aws_route53_zone.paradise_cakes.zone_id
  name    = var.environment == "prod" ? "api.paradisecakesbymegan.com" : "dev-api.paradisecakesbymegan.com"
  type    = "NS"
  ttl     = 300

  records = [
    data.aws_route53_zone.paradise_cakes_api.name_servers[0],
    data.aws_route53_zone.paradise_cakes_api.name_servers[1],
    data.aws_route53_zone.paradise_cakes_api.name_servers[2],
    data.aws_route53_zone.paradise_cakes_api.name_servers[3],
  ]
}
