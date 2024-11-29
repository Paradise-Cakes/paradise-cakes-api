resource "aws_acm_certificate" "paradise_cakes" {
  domain_name       = var.environment == "prod" ? "api.megsparadisecakes.com" : "dev-api.megsparadisecakes.com"
  validation_method = "DNS"
}
