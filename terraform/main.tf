terraform {
  backend "s3" {
    bucket = "paradise-cakes-api-tfstate"
    key    = "paradise-cakes-api.tfstate"
    region = "us-east-1"
  }
}