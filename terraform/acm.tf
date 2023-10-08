resource "aws_acm_certificate" "cakes_api_tech" {
  domain_name       = "cakes.api.tech"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_acm_certificate_validation" "cakes_api_tech" {
  certificate_arn = aws_acm_certificate.cakes_api_tech.arn
}

resource "aws_acm_certificate" "api" {
  domain_name       = "cakes-us-east-1.api.tech"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_acm_certificate_validation" "api" {
  certificate_arn = aws_acm_certificate.api.arn
}