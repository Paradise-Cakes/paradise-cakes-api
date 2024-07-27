resource "aws_acm_certificate" "paradise_cakes_cloud" {
  domain_name       = var.environment == "prod" ? "paradisecakes.cloud" : "paradisecakes-dev.cloud"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_acm_certificate_validation" "paradise_cakes_cloud" {
  certificate_arn = aws_acm_certificate.paradise_cakes_cloud.arn
}
