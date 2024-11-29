data "aws_route53_zone" "paradise_cakes_api" {
  name = var.environment == "prod" ? "api.megsparadisecakes.com" : "dev-api.megsparadisecakes.com"
}

data "aws_route53_zone" "paradise_cakes" {
  name = var.environment == "prod" ? "megsparadisecakes.com" : "dev.megsparadisecakes.com"
}
