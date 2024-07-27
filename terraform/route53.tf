data "aws_route53_zone" "hosted_zone" {
  name = "paradisecakes.cloud"
}

data "aws_route53_zone" "hosted_zone_dev" {
  name = "paradisecakes-dev.cloud"
}

resource "aws_route53_record" "main" {
  zone_id = data.aws_route53_zone.hosted_zone.zone_id
  name    = "paradisecakes.cloud"
  type    = "A"

  alias {
    name                   = aws_api_gateway_domain_name.paradise_cakes_cloud.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.paradise_cakes_cloud.cloudfront_zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "dev" {
  zone_id = data.aws_route53_zone.hosted_zone_dev.zone_id
  name    = "paradisecakes-dev.cloud"
  type    = "A"

  alias {
    name                   = aws_api_gateway_domain_name.paradise_cakes_cloud_dev.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.paradise_cakes_cloud_dev.cloudfront_zone_id
    evaluate_target_health = true
  }
}
