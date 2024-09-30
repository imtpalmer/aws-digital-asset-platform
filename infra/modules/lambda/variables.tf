variable "aws_region" {
  description = "The AWS region in which the Lambda functions will be created"
  type        = string
}

variable "lambda_execution_role_arn" {
  description = "IAM role that the Lambda functions will use for execution"
  type        = string
}

variable "python_runtime" {
  description = "Runtime environment for the Lambda functions (e.g., python3.9)"
  type        = string
}

variable "lambdas" {
  description = "Map of Lambda functions to create with handlers and environment variables"
  type = map(object({
    handler               = string
    environment_variables = map(string)
    description           = string
    use_klayers           = optional(bool, false) # Optional, defaults to false
  }))
}

variable "timeout" {
  description = "The amount of time your Lambda function has to run in seconds"
  type        = number
  default     = 30
}

variable "memory_size" {
  description = "Amount of memory in MB your Lambda function can use at runtime"
  type        = number
  default     = 128
}