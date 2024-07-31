resource "aws_acm_certificate" "paradise_cakes" {
  domain_name       = "api.paradisecakesbymegan.com"
  validation_method = "DNS"
}

data "aws_acm_certificate" "paradise_cakes_dev" {
  domain = "dev-api.paradisecakesbymegan.com"
}

resource "aws_acm_certificate_validation" "paradise_cakes" {
  certificate_arn = aws_acm_certificate.paradise_cakes.arn
}
