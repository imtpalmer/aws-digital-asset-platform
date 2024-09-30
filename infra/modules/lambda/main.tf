terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0" # Use a version that supports OAC
    }
    klayers = {
      source  = "ldcorentin/klayer"
      version = "~> 1.0.0"
    }
  }
}

data "klayers_package_latest_version" "cryptography" {
  name   = "cryptography"
  region = var.aws_region
}

# Lambda function resource that dynamically creates multiple Lambda functions
resource "aws_lambda_function" "lambda_functions" {
  for_each = var.lambdas

  function_name = each.key                      # Lambda function name from the map key
  handler       = each.value.handler            # Handler from the lambdas map
  runtime       = var.python_runtime            # Lambda runtime passed to the module
  role          = var.lambda_execution_role_arn # IAM role for Lambda execution

  environment {
    variables = each.value.environment_variables # Environment variables for each Lambda
  }

  # The source code for the Lambda function (zip file)
  source_code_hash = filebase64sha256("${path.root}/../lambdas/build/${each.key}.zip")
  filename         = "${path.root}/../lambdas/build/${each.key}.zip" # Location of the zip file

  # Conditionally include the klayers package if use_klayers is true
  layers = each.value.use_klayers ? [data.klayers_package_latest_version.cryptography.arn] : []

  # Optional settings
  timeout     = var.timeout
  memory_size = var.memory_size
  description = each.value.description
}
