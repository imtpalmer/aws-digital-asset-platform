variable "react_bucket_regional_domain_name" {
  description = "the react apps regional domain name"
  type        = string
}
variable "environment" {
  description = "Variable passed in from root defining the environment (e.g., dev, prod, staging)"
  type        = string
}
