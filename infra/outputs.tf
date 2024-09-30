output "api_gateway_v2_url" {
  value = module.api_gateway.api_gateway_v2_url
}

# Output for API Gateway v2 URLs
output "api_gateway_v2_urls" {
  value = module.api_gateway.api_gateway_v2_urls
}

# Output for API Gateway Routes
output "api_gateway_routes" {
  value = module.api_gateway.api_gateway_routes
}

output "react_app_s3_bucket" {
  description = "ARNs of the Lambda functions"
  value       = local.digital_assets_react_bucket_name
}

output "cloudfront_distribution_id" {
  value       = module.cloudfront.cloudfront_distribution_id
}
output "cloudfront_distribution_arn" {
  value       = module.cloudfront.cloudfront_distribution_arn
}

output "react_app_url" {
    value = module.cloudfront.cloudfront_distribution_url
}