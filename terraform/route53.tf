data "aws_route53_zone" "hosted_zone" {
  name = var.environment == "prod" ? "paradisecakes.cloud" : "paradisecakes-dev.cloud"
}


resource "aws_route53_record" "main" {
  zone_id = data.aws_route53_zone.hosted_zone.zone_id
  name    = var.environment == "prod" ? "paradisecakes.cloud" : "paradisecakes-dev.cloud"
  type    = "A"

  alias {
    name                   = aws_api_gateway_domain_name.paradise_cakes_cloud.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.paradise_cakes_cloud.cloudfront_zone_id
    evaluate_target_health = true
  }
}
