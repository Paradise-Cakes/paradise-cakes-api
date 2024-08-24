data "aws_route53_zone" "paradise_cakes_api" {
  name = var.environment == "prod" ? "api.paradisecakesbymegan.com" : "dev-api.paradisecakesbymegan.com"
}
