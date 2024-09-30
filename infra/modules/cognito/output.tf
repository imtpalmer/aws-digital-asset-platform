output "cognito_user_pool_id" {
  description = "user pool id used by the lambdas"
  value       = aws_cognito_user_pool.user_pool.id
}

output "cognito_user_pool_arn" {
  description = "user pool id used by the lambdas"
  value       = aws_cognito_user_pool.user_pool.arn
}

output "cognito_user_pool_client_id" {
  description = "user pool id used by the lambdas"
  value       = aws_cognito_user_pool_client.user_pool_client.id
}