variable "digital_assets_bucket_name" {
  description = "Name of the S3 bucket to store all uploaded digital assets"
  type        = string
}

variable "digital_assets_react_bucket_name" {
  description = "Name of the S3 bucket to host the React app"
  type        = string
}

variable "environment" {
  description = "Variable passed in from root defining the environment (e.g., dev, prod, staging)"
  type        = string
}

variable "cloudfront_distribution_arn" {
  description = "CloudFront distribution ARN"
  type        = string
}