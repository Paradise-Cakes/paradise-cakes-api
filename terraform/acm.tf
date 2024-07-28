data "aws_acm_certificate" "paradise_cakes_cloud" {
  domain = var.environment == "prod" ? "paradisecakes.cloud" : "paradisecakes-dev.cloud"
}
