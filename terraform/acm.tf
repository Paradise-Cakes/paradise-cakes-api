data "aws_acm_certificate" "paradise_cakes" {
  domain = var.environment == "prod" ? "paradisecakesbymegan.com" : "dev.paradisecakesbymegan.com"
}

resource "aws_acm_certificate_validation" "paradise_cakes" {
  certificate_arn = data.aws_acm_certificate.paradise_cakes.arn
}
