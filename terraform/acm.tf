resource "aws_acm_certificate" "paradise_cakes_cloud" {
  domain_name       = "paradisecakes.cloud"
  validation_method = "DNS"
}

resource "aws_acm_certificate_validation" "paradise_cakes_cloud" {
  certificate_arn = aws_acm_certificate.paradise_cakes_cloud.arn
}
