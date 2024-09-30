output "api_gateway_v2_url" {
  description = "The base URL for the api gateway v2"
  value       = aws_apigatewayv2_api.api_gateway_v2.api_endpoint
}

# Output for API Gateway v2 URLs
output "api_gateway_v2_urls" {
  value = aws_apigatewayv2_api.api_gateway_v2.api_endpoint
}

# Output for API Gateway Routes
output "api_gateway_routes" {
  value = [
    for route in aws_apigatewayv2_route.lambda_options_routes :
    {
      route_key   = route.route_key
      http_method = "OPTIONS"
    }
  ]
}