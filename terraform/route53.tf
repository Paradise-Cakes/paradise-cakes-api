data "aws_route53_zone" "paradise_cakes_api" {
  name = var.environment == "prod" ? "api.paradisecakesbymegan.com" : "dev-api.paradisecakesbymegan.com"
}

# resource "aws_route53_record" "api_record" {
#   zone_id = data.aws_route53_zone.paradise_cakes_api.zone_id
#   name    = var.environment == "prod" ? "api.paradisecakesbymegan.com" : "dev-api.paradisecakesbymegan.com"
#   type    = "A"

#   alias {
#     name                   = module.api_gateway.cloudfront_domain_name
#     zone_id                = module.api_gateway.cloudfront_zone_id
#     evaluate_target_health = true
#   }
# }

# resource "aws_route53_record" "paradise_cakes_validation_record" {
#   for_each = {
#     for dvo in aws_acm_certificate.paradise_cakes.domain_validation_options : dvo.domain_name => {
#       name    = dvo.resource_record_name
#       record  = dvo.resource_record_value
#       type    = dvo.resource_record_type
#       zone_id = data.aws_route53_zone.paradise_cakes_api.zone_id
#     }
#   }

#   allow_overwrite = true
#   name            = each.value.name
#   records         = [each.value.record]
#   ttl             = 60
#   type            = each.value.type
#   zone_id         = each.value.zone_id
# }

data "aws_route53_zone" "paradise_cakes" {
  count        = var.environment == "prod" ? 1 : 0
  name         = "paradisecakesbymegan.com"
  private_zone = false
}

# resource "aws_route53_record" "paradise_cakes_api_ns" {
#   count   = var.environment == "prod" ? 1 : 0
#   zone_id = data.aws_route53_zone.paradise_cakes[0].zone_id
#   name    = "api.paradisecakesbymegan.com"
#   type    = "NS"
#   ttl     = 300

#   records = data.aws_route53_zone.paradise_cakes_api.name_servers
# }

# resource "aws_route53_record" "paradise_cakes_dev_api_ns" {
#   count   = var.environment == "prod" ? 1 : 0
#   zone_id = data.aws_route53_zone.paradise_cakes[0].zone_id
#   name    = "dev-api.paradisecakesbymegan.com"
#   type    = "NS"
#   ttl     = 300

#   records = [
#     "ns-510.awsdns-63.com",
#     "ns-1870.awsdns-41.co.uk",
#     "ns-647.awsdns-16.net",
#     "ns-1266.awsdns-30.org"
#   ]
# }
