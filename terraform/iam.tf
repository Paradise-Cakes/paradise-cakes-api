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

resource "aws_iam_role_policy" "paradise_cakes_api_role_policy" {
  name = "paradise-cakes-api-role_policy"
  role = aws_iam_role.paradise_cakes_api_role.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction",
      ],
      "Resource": "*"
    }
  ]
}
EOF
}
