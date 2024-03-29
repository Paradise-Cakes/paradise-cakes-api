data "aws_caller_identity" "current" {}

terraform {
  backend "s3" {
    bucket = "paradise-cakes-api-tfstate"
    key    = "paradise-cakes-api.tfstate"
    region = "us-east-1"
  }
}