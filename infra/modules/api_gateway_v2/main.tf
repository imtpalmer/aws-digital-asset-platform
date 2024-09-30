# Create the API Gateway
resource "aws_apigatewayv2_api" "api_gateway_v2" {
  name          = var.api_gateway_name
  protocol_type = "HTTP"

  # Removed cors_configuration since you prefer handling CORS in Lambda
  /*
  cors_configuration {
    allow_origins  = ["*"]
    allow_methods  = ["GET", "POST", "OPTIONS"]
    allow_headers  = ["Content-Type", "Authorization", "X-Requested-With", "X-CSRF-Token", "Content-Security-Policy", "x-amz-meta-*"]
    expose_headers = ["Location", "X-Request-ID", "ETag", "Content-Security-Policy", "x-amz-meta-*"]
    max_age        = 3600 # Cache preflight response for 1 hours
  }*/
}

# Create the Deployment
resource "aws_apigatewayv2_deployment" "api_gateway_v2_deployment" {
  api_id = aws_apigatewayv2_api.api_gateway_v2.id

  depends_on = [
    aws_apigatewayv2_route.lambda_post_routes,
    aws_apigatewayv2_route.lambda_options_routes,
    aws_apigatewayv2_integration.lambda_integrations,
  ]
}

# Create the Stage
resource "aws_apigatewayv2_stage" "api_gateway_v2_stage" {
  api_id        = aws_apigatewayv2_api.api_gateway_v2.id
  deployment_id = aws_apigatewayv2_deployment.api_gateway_v2_deployment.id
  name          = var.environment
  auto_deploy   = false
}

# Local variable mapping function names to Lambda function objects
locals {
  lambda_function_map = {
    for lambda in var.lambda_functions : lambda.name => lambda
  }
}

# Create API Gateway Integrations
resource "aws_apigatewayv2_integration" "lambda_integrations" {
  for_each = local.lambda_function_map

  api_id                 = aws_apigatewayv2_api.api_gateway_v2.id
  integration_type       = "AWS_PROXY"
  integration_uri        = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${each.value.arn}/invocations"
  payload_format_version = "2.0"
}

# Create POST Routes for each Lambda
resource "aws_apigatewayv2_route" "lambda_post_routes" {
  for_each = aws_apigatewayv2_integration.lambda_integrations

  api_id    = aws_apigatewayv2_api.api_gateway_v2.id
  route_key = "POST /${each.key}"
  target    = "integrations/${each.value.id}"
}

# Create OPTIONS Routes for each Lambda (for CORS)
resource "aws_apigatewayv2_route" "lambda_options_routes" {
  for_each = aws_apigatewayv2_integration.lambda_integrations

  api_id    = aws_apigatewayv2_api.api_gateway_v2.id
  route_key = "OPTIONS /${each.key}"
  target    = "integrations/${each.value.id}"
}

# Grant API Gateway permission to invoke each Lambda function
resource "aws_lambda_permission" "lambda_permissions" {
  for_each = local.lambda_function_map

  statement_id  = "AllowExecutionFromAPIGateway-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = each.value.name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api_gateway_v2.execution_arn}/*/*"
}
