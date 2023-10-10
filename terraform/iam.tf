data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "paradise_cakes_api_role" {
  name               = "paradise-cakes-api-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}
