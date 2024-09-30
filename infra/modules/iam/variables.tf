
variable "digital_assets_bucket_name" {
  description = "The Assets S3 Bucket name"
  type        = string
}

variable "digital_assets_react_bucket_name" {
  description = "The S3 Bucket for hosting the React App"
  type        = string
}

variable "dynamodb_table_name" {
  description = "The table used to store all of the assets metadata"
  type        = string
}

variable "lambda_role_name" {
  description = "The name of the lambda exec role"
  type = string
}

variable "aws_region" {
  type = string
}

variable "cognito_user_pool_arn" {
  type = string
}