data "aws_route53_zone" "paradise_cakes_api" {
  name = var.environment == "prod" ? "api.megsparadisecakes.com" : "dev-api.megsparadisecakes.com"
}
