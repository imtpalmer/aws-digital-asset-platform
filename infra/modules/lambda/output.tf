# Output the ARNs of the created Lambda functions
output "lambda_function_arns" {
  value = { for k, lambda in aws_lambda_function.lambda_functions : k => lambda.arn }
}

# Output the names and ARNs of the created Lambda functions using the splat operator
output "lambda_functions" {
  value = [
    for index, lambda in aws_lambda_function.lambda_functions :
    {
      name       = lambda.function_name,
      arn        = lambda.arn,
      invoke_arn = lambda.invoke_arn
    }
  ]
}