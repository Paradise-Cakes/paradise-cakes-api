resource "aws_cognito_user_pool_client" "paradise_cakes_client" {
  name         = "paradise-cakes-client"
  user_pool_id = aws_cognito_user_pool.paradise_cakes_user_pool.id

  generate_secret = false

  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
  ]
}

resource "aws_cognito_user_pool" "paradise_cakes_user_pool" {
  name = "paradise-cakes-user-pool"

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  username_attributes        = ["email"]
  auto_verified_attributes   = ["email"]
  sms_authentication_message = "Your code is {####}"

  device_configuration {
    challenge_required_on_new_device      = true
    device_only_remembered_on_user_prompt = true
  }

  email_configuration {
    email_sending_account = "DEVELOPER"
    source_arn            = "arn:aws:ses:us-east-1:${data.aws_caller_identity.current.account_id}:identity/do-not-reply@paradisecakesbymegan.com"
    from_email_address    = "do-not-reply@paradisecakesbymegan.com"
  }

  schema {
    name                = "given_name"
    attribute_data_type = "String"
    mutable             = true
    required            = false
    string_attribute_constraints {
      min_length = "1"
      max_length = "50"
    }
  }

  schema {
    name                = "family_name"
    attribute_data_type = "String"
    mutable             = true
    required            = false
    string_attribute_constraints {
      min_length = "1"
      max_length = "50"
    }
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
    recovery_mechanism {
      name     = "verified_phone_number"
      priority = 2
    }
  }
}

resource "aws_cognito_user_group" "paradise_cakes_admin_group" {
  name         = "paradise-cakes-admin-group"
  description  = "paradise cakes admin group"
  user_pool_id = aws_cognito_user_pool.paradise_cakes_user_pool.id
}

resource "aws_cognito_user_pool" "dev_paradise_cakes_user_pool" {
  name = "dev-paradise-cakes-user-pool"

  admin_create_user_config {
    allow_admin_create_user_only = true
  }

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  mfa_configuration = "OFF" # or "ON" if you want MFA

  schema {
    name                = "email"
    attribute_data_type = "String"
    mutable             = false
    required            = true
  }

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]
}

resource "aws_cognito_user_pool_client" "dev_paradise_cakes_client" {
  name         = "dev-paradise-cakes-client"
  user_pool_id = aws_cognito_user_pool.dev_paradise_cakes_user_pool.id

  generate_secret = false

  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
  ]

  allowed_oauth_flows_user_pool_client = true

  allowed_oauth_flows = [
    "code",
    "implicit",
  ]

  allowed_oauth_scopes = [
    "openid",
    "profile",
    "email",
  ]

  callback_urls = [
    "https://dev.paradisecakesbymegan.com/callback",
  ]

  logout_urls = [
    "https://dev.paradisecakesbymegan.com/logout",
  ]

  supported_identity_providers = [
    "COGNITO",
  ]
}

resource "aws_cognito_user_pool_domain" "dev_user_pool_domain" {
  domain       = "dev-paradisecakesbymegan"
  user_pool_id = aws_cognito_user_pool.dev_paradise_cakes_user_pool.id
}
