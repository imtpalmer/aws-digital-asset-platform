provider "aws" {
  region = var.aws_region
}

# IAM Policy Module
module "iam" {
  source                           = "./modules/iam"
  digital_assets_bucket_name       = local.digital_assets_bucket_name       # used to assign IAM Role/Policies
  digital_assets_react_bucket_name = local.digital_assets_react_bucket_name # same as above
  dynamodb_table_name              = local.dynamodb_table_name
  lambda_role_name                 = local.lambda_role_name
  aws_region                       = var.aws_region
  cognito_user_pool_arn            = module.cognito.cognito_user_pool_arn
}

# S3 Module
module "s3" {
  source                           = "./modules/s3"
  digital_assets_bucket_name       = local.digital_assets_bucket_name
  digital_assets_react_bucket_name = local.digital_assets_react_bucket_name
  cloudfront_distribution_arn      = module.cloudfront.cloudfront_distribution_arn
  environment                      = var.environment # Passing local environment to the module
}

# CloudFront Module
module "cloudfront" {
  source                            = "./modules/cloudfront"
  react_bucket_regional_domain_name = module.s3.react_bucket_regional_domain_name
  environment                       = var.environment # Passing local environment to the module
}

# DynamoDB Module
module "dynamodb" {
  source      = "./modules/dynamodb"
  table_name  = local.dynamodb_table_name
  environment = var.environment # Passing local environment to the module
}

# Cognito Module
module "cognito" {
  source                = "./modules/cognito"
  user_pool_name        = local.cognito_user_pool_name
  user_pool_client_name = local.cognito_user_pool_client_name
  environment           = var.environment # Passing local environment to the module
}

# API Gateway Module
module "api_gateway" {
  source                      = "./modules/api_gateway_v2"
  api_gateway_name            = local.api_gateway_name
  environment                 = var.environment # Passing local environment to the module
  lambda_functions            = module.lambda.lambda_functions
  cloudfront_distribution_url = module.cloudfront.cloudfront_distribution_url
  aws_region                  = var.aws_region

  depends_on = [module.lambda]
}

# Lambda Module (updated for all Lambdas)
module "lambda" {
  source                    = "./modules/lambda"
  aws_region                = var.aws_region
  lambda_execution_role_arn = module.iam.lambda_execution_role_arn
  python_runtime            = var.python_runtime

  lambdas = {
    "register" = {
      description = ""
      handler     = "register.lambda_handler"
      use_klayers = false
      environment_variables = {
        COGNITO_USER_POOL_CLIENT_ID = module.cognito.cognito_user_pool_client_id
      }
    }
    "confirm_registration" = {
      handler     = "confirm_registration.lambda_handler"
      description = ""
      use_klayers = false
      environment_variables = {
        COGNITO_USER_POOL_ID        = module.cognito.cognito_user_pool_id
        COGNITO_USER_POOL_CLIENT_ID = module.cognito.cognito_user_pool_client_id
      }
    }
    "resend_confirmation_code" = {
      handler     = "resend_confirmation_code.lambda_handler"
      description = ""
      use_klayers = false
      environment_variables = {
        COGNITO_USER_POOL_CLIENT_ID = module.cognito.cognito_user_pool_client_id
      }
    }
    "login" = {
      handler     = "login.lambda_handler"
      description = ""
      use_klayers = false
      environment_variables = {
        COGNITO_USER_POOL_ID        = module.cognito.cognito_user_pool_id
        COGNITO_USER_POOL_CLIENT_ID = module.cognito.cognito_user_pool_client_id
      }
    }
    "upload_asset" = {
      handler     = "upload_asset.lambda_handler"
      description = ""
      use_klayers = true
      environment_variables = {
        DIGITAL_ASSETS_BUCKET_NAME = local.digital_assets_bucket_name
        DYNAMODB_TABLE_NAME        = local.dynamodb_table_name
        COGNITO_USER_POOL_ID       = module.cognito.cognito_user_pool_id
      }
    }
    "view_asset" = {
      handler     = "view_asset.lambda_handler"
      description = ""
      use_klayers = true
      environment_variables = {
        DIGITAL_ASSETS_BUCKET_NAME = local.digital_assets_bucket_name
        COGNITO_USER_POOL_ID       = module.cognito.cognito_user_pool_id
      }
    }
    "list_assets" = {
      handler     = "list_assets.lambda_handler"
      description = ""
      use_klayers = true
      environment_variables = {
        DYNAMODB_TABLE_NAME  = module.dynamodb.dynamodb_table_name
        COGNITO_USER_POOL_ID = module.cognito.cognito_user_pool_id
      }
    }
    "delete_asset" = {
      handler     = "delete_asset.lambda_handler"
      description = ""
      use_klayers = true
      environment_variables = {
        DIGITAL_ASSETS_BUCKET_NAME = local.digital_assets_bucket_name
        DYNAMODB_TABLE_NAME        = module.dynamodb.dynamodb_table_name
        COGNITO_USER_POOL_ID       = module.cognito.cognito_user_pool_id
      }
    }
    "update_asset" = {
      handler     = "update_asset.lambda_handler"
      description = ""
      use_klayers = true
      environment_variables = {
        DIGITAL_ASSETS_BUCKET_NAME = local.digital_assets_bucket_name
        DYNAMODB_TABLE_NAME        = module.dynamodb.dynamodb_table_name
        COGNITO_USER_POOL_ID       = module.cognito.cognito_user_pool_id
      }
    }
    "multipart_start_upload" = {
      handler     = "multipart_start_upload.lambda_handler"
      description = ""
      use_klayers = true
      environment_variables = {
        DIGITAL_ASSETS_BUCKET_NAME = local.digital_assets_bucket_name
        COGNITO_USER_POOL_ID       = module.cognito.cognito_user_pool_id
      }
    }
    "multipart_generate_presigned_urls" = {
      handler     = "multipart_generate_presigned_urls.lambda_handler"
      description = ""
      use_klayers = true
      environment_variables = {
        DIGITAL_ASSETS_BUCKET_NAME = local.digital_assets_bucket_name
        COGNITO_USER_POOL_ID       = module.cognito.cognito_user_pool_id
      }
    }
    "multipart_complete_upload" = {
      handler     = "multipart_complete_upload.lambda_handler"
      description = ""
      use_klayers = true
      environment_variables = {
        DIGITAL_ASSETS_BUCKET_NAME = local.digital_assets_bucket_name
        COGNITO_USER_POOL_ID       = module.cognito.cognito_user_pool_id
      }
    }
  }
  depends_on = [module.iam]
}
resource "null_resource" "deploy_react_app" {
  provisioner "local-exec" {
    when    = create
    command = <<EOT
    cd ../scripts
    ./build-react-app.sh
    EOT
  }

  # To ensure this runs after apply
  depends_on = [
    module.s3, module.api_gateway, module.cloudfront,
    module.cognito, module.dynamodb, module.iam, module.lambda
  ]
}

resource "null_resource" "delete_s3_objects" {
  provisioner "local-exec" {
    when    = destroy
    command = <<EOT
      aws s3 rm s3://${self.triggers.bucket_name} --recursive
    EOT
  }

  triggers = {
    bucket_name = local.digital_assets_react_bucket_name
  }
}
