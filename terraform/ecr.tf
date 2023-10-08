resource "aws_ecr_repository" "paradise_cakes_api_lambda" {
  name                 = "paradise-cakes-api-lambdas-us-east-1"
  image_tag_mutability = "MUTABLE"
  encryption_configuration {
    encryption_type = "AES256"
  }

  image_scanning_configuration {
    scan_on_push = true
  }
}