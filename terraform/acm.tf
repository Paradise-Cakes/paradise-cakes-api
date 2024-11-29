data "aws_acm_certificate" "paradise_cakes" {
  domain      = var.environment == "prod" ? "api.megsparadisecakes.com" : "dev-api.megsparadisecakes.com"
  types       = ["AMAZON_ISSUED"]
  most_recent = true
}
