variable "environment" {
  description = "Variable passed in from root defining the environment (e.g., dev, prod, staging)"
  type        = string
}

variable "api_gateway_name" {
  description = "This is the name of the API gateway V2"
  type        = string
}

variable "aws_region" {
  type = string
}

variable "cloudfront_distribution_url" {
  type = string
}

# the list of lambdas
variable "lambda_functions" {
  description = "List of Lambda function names and ARNs"
  type = list(object({
    name       = string
    arn        = string
    invoke_arn = string
  }))
}
