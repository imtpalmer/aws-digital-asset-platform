resource "aws_cognito_user_pool" "user_pool" {
  name = var.user_pool_name

  auto_verified_attributes   = ["email"]
  email_verification_subject = "Digital Asset Platform verification code"
  email_verification_message = "Your Digital Asset Platform verification code is {####}"

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_uppercase = true
    require_numbers   = true
    require_symbols   = false
  }

  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  schema {
    attribute_data_type = "String"
    name                = "email"
    required            = true
    mutable             = false
  }
}

resource "aws_cognito_user_pool_client" "user_pool_client" {
  name         = var.user_pool_client_name
  user_pool_id = aws_cognito_user_pool.user_pool.id

   explicit_auth_flows = [
    "ADMIN_NO_SRP_AUTH",
    "USER_PASSWORD_AUTH"
  ]

  prevent_user_existence_errors = "ENABLED"
}