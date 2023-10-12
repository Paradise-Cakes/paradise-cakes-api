data "aws_route53_zone" "hosted_zone" {
  name = "paradisecakes.cloud"
}

resource "aws_route53_record" "www" {
  zone_id = data.aws_route53_zone.hosted_zone.zone_id
  name    = "www.paradisecakes.cloud"
  type    = "A"

  alias {
    name                   = aws_lb.paradise_cakes_lb.dns_name
    zone_id                = aws_lb.paradise_cakes_lb.zone_id
    evaluate_target_health = true
  }
}
