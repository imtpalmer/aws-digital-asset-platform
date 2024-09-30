
variable "table_name" {
  description = "Passed variable from the root module defning the name for the dynamodb table name"
  type        = string
}

variable "environment" {
  description = "Variable passed in from root defining the environment (e.g., dev, prod, staging)"
  type        = string
}
