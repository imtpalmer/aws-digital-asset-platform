variable "aws_region" {
  default = "us-east-1"
}

variable "environment" {
  description = "The environment (e.g., dev, prod, staging)"
  default     = "dev" # Change when applying in other environments
}

variable "python_runtime" {
  description = "the default runtime for Python Lambdas"
  default     = "python3.9"
}

variable "appname" {
  description = "The name of the application"
  type        = string
  default     = "digital-assets"
}

# S3 bucket base names
variable "assets_bucket_base_name" {
  description = "Base name for the S3 bucket storing assets"
  default     = "bucket-0101"
}

variable "react_bucket_base_name" {
  description = "Base name for the S3 bucket hosting the React app"
  default     = "react-bucket-0101"
}

# DynamoDB table base name
variable "dynamodb_table_base_name" {
  description = "Base name for DynamoDB table storing metadata"
  default     = "metadata"
}

# Cognito user pool base names
variable "cognito_user_pool_base_name" {
  description = "Base name for the Cognito User Pool"
  default     = "user-pool"
}

variable "cognito_user_pool_client_base_name" {
  description = "Base name for the Cognito User Pool Client"
  default     = "user-pool-client"
}

# API Gateway base name
variable "api_gateway_base_name" {
  description = "Base name for the API Gateway"
  default     = "api-gateway"
}

# CloudFront distribution base-name
variable "cloudfront_distrubution_base_name" {
  description = "Base name for Lambda execution role"
  default     = "cloudfront-distribution-name"
}

variable "cloudfront_distrubution_cors_policy_base_name" {
  description = "base name for the cors_policy"
  default     = "cloudfront-distribution-cors-policy"
}

# Lambda role base name
variable "lambda_role_base_name" {
  description = "Base name for Lambda execution role"
  default     = "lambda-exec-role"
}
