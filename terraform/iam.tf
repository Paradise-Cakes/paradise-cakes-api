resource "aws_iam_role" "lambda_execution_role" {
  name = "lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "paradise_cakes_api_policy" {
  name        = "paradise-cakes-api-policy"
  description = "paradise cakes api policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "execute-api:Invoke"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:execute-api:us-east-1:${data.aws_caller_identity.current.account_id}:*/*/*/*"
      },
      {
        Action   = "lambda:InvokeFunction",
        Effect   = "Allow",
        Resource = aws_lambda_function.app.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "api_gateway_attachment" {
  policy_arn = aws_iam_policy.paradise_cakes_api_policy.arn
  role       = aws_iam_role.lambda_execution_role.name
}
