
# Retch AWS account identity details
data "aws_caller_identity" "current" {}

# Note: utilizing a single IAM Role for Lambda with specific resource access
resource "aws_iam_role" "lambda_exec_role" {
  name = "${var.lambda_role_name}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# This is a general polciy for all of the lambdas, in the future this should be scoped down.
resource "aws_iam_policy" "lambda_policy" {
  name = "${var.lambda_role_name}_policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"
      },
      {
        Effect = "Allow",
        Action = [
          "dynamodb:PutItem", "dynamodb:GetItem", "dynamodb:UpdateItem", "dynamodb:DeleteItem", "dynamodb:Query",
          "s3:PutObject", "s3:GetObject", "s3:DeleteObject", "s3:CreateMultipartUpload",
          "cognito-idp:AdminCreateUser", "cognito-idp:AdminInitiateAuth", "cognito-idp:AdminDeleteUser",
          "kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey", "kms:GenerateDataKeyWithoutPlaintext", "kms:ReEncrypt*"
        ],
        Resource = [
          "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.dynamodb_table_name}",
          "arn:aws:kms:${var.aws_region}:${data.aws_caller_identity.current.account_id}:key/*",
          "arn:aws:s3:::${var.digital_assets_bucket_name}/*",
          "${var.cognito_user_pool_arn}"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}