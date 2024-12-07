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
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:PostLogEvents",
        ],
        Effect   = "Allow",
        Resource = "*"
      },
      {
        Action   = "dynamodb:Query",
        Effect   = "Allow",
        Resource = "arn:aws:dynamodb:us-east-1:${data.aws_caller_identity.current.account_id}:table/desserts/index/dessert-type-index"
      },
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:UpdateItem",
          "dynamodb:Scan",
          "dynamodb:Query"
          "dynamodb:BatchWriteItem"
          "dynamodb:BatchGetItem"
        ]
        Effect   = "Allow",
        Resource = "arn:aws:dynamodb:us-east-1:${data.aws_caller_identity.current.account_id}:table/*"
      },
      {
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:DeleteObject",
        ]
        Effect = "Allow",
        Resource = [
          "arn:aws:s3:::paradise-cakes-images",
          "arn:aws:s3:::paradise-cakes-images/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "api_gateway_attachment" {
  policy_arn = aws_iam_policy.paradise_cakes_api_policy.arn
  role       = aws_iam_role.lambda_execution_role.name
}

data "aws_iam_policy_document" "user_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    principals {
      type        = "Federated"
      identifiers = ["cognito-idp.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "cognito-identity.amazonaws.com:aud"
      values   = [aws_cognito_identity_pool.orders_identity_pool.id]
    }
  }
}

data "aws_iam_policy_document" "admin_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    effect = "Allow"

    principals {
      type        = "Federated"
      identifiers = ["cognito-identity.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "cognito-identity.amazonaws.com:aud"
      values   = [aws_cognito_identity_pool.orders_identity_pool.id]
    }
  }
}

resource "aws_iam_role" "user_role" {
  name               = "user-role"
  assume_role_policy = data.aws_iam_policy_document.user_assume_role_policy.json
}

resource "aws_iam_role" "admin_role" {
  name               = "admin-role"
  assume_role_policy = data.aws_iam_policy_document.admin_assume_role_policy.json
}

resource "aws_iam_policy" "user_order_access_policy" {
  name        = "user-order-access-policy"
  description = "Policy for users to access their own orders in DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Resource = "arn:aws:dynamodb:us-east-1:${data.aws_caller_identity.current.account_id}:table/orders"
        Condition = {
          "ForAllValues:StringEquals" = {
            "dynamodb:LeadingKeys" = [format("cognito-identity.amazonaws.com:%s", "sub")]
          }
        }
      }
    ]
  })
}

resource "aws_iam_policy" "admin_order_access_policy" {
  name        = "admin-order-access-policy"
  description = "Policy for admins to access all orders in DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:Scan",
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Resource = "arn:aws:dynamodb:us-east-1:${data.aws_caller_identity.current.account_id}:table/orders"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "user_order_access_attachment" {
  policy_arn = aws_iam_policy.user_order_access_policy.arn
  role       = aws_iam_role.user_role.name
}

resource "aws_iam_role_policy_attachment" "admin_order_access_attachment" {
  policy_arn = aws_iam_policy.admin_order_access_policy.arn
  role       = aws_iam_role.admin_role.name
}
