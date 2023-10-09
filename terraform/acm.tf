resource "aws_acm_certificate" "paradise_cakes_cloud" {
  domain_name       = "api.paradisecakes.cloud"
  validation_method = "DNS"
}

data "aws_route53_zone" "paradise_cakes_cloud" {
  name         = "paradisecakes.cloud"
  private_zone = false
}

resource "aws_route53_record" "paradise_cakes_cloud" {
  for_each = {
    for dvo in aws_acm_certificate.paradise_cakes_cloud.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.paradise_cakes_cloud.zone_id
}

resource "aws_acm_certificate_validation" "paradise_cakes_cloud" {
  certificate_arn         = aws_acm_certificate.paradise_cakes_cloud.arn
  validation_record_fqdns = [for record in aws_route53_record.paradise_cakes_cloud : record.fqdn]
}