locals {

  # S3 bucket names
  digital_assets_bucket_name = "${var.environment}-${var.appname}-${var.assets_bucket_base_name}"
  digital_assets_react_bucket_name = "${var.environment}-${var.appname}-${var.react_bucket_base_name}"

  # DynamoDB table name
  dynamodb_table_name = "${var.environment}-${var.appname}-${var.dynamodb_table_base_name}"

  # Cognito user pool names
  cognito_user_pool_name        = "${var.environment}-${var.appname}-${var.cognito_user_pool_base_name}"
  cognito_user_pool_client_name = "${var.environment}-${var.appname}-${var.cognito_user_pool_client_base_name}"

  # API Gateway name
  api_gateway_name = "${var.environment}-${var.appname}-${var.api_gateway_base_name}"

  # Lambda role name
  lambda_role_name = "${var.environment}-${var.appname}-${var.lambda_role_base_name}"

  # CloudFront distribution name
  cloudfront_distribution_name = "${var.environment}-${var.appname}-${var.cloudfront_distrubution_base_name}"
}