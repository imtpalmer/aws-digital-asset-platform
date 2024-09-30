variable "environment" {
  description = "Variable passed in from root defining the environment (e.g., dev, prod, staging)"
  type        = string
}

variable "user_pool_name" {
  description = "Variable passed in from root defining the environment (e.g., dev, prod, staging)"
  type        = string
}

variable "user_pool_client_name" {
  description = "Variable passed in from root defining the environment (e.g., dev, prod, staging)"
  type        = string
}