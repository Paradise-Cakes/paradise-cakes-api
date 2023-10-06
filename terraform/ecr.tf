resource "aws_ecr_repository" "pc_respository" {
  name                 = "pc-ecr-repository"
  image_tag_mutability = "IMMUTABLE"
}