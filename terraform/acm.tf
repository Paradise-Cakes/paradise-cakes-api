resource "aws_acm_certificate" "paradise_cakes_cloud" {
  domain_name       = "api.paradisecakes.cloud"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

data "aws_route53_zone" "public" {
  name         = "paradisecakes.cloud"
  private_zone = false
}

resource "aws_acm_certificate_validation" "paradise_cakes_cloud" {
  certificate_arn = aws_acm_certificate.paradise_cakes_cloud.arn
}