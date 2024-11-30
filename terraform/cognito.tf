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
    source_arn            = "arn:aws:ses:us-east-1:132899756990:identity/do-not-reply@megsparadisecakes.com"
    from_email_address    = "do-not-reply@megsparadisecakes.com"
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

resource "aws_cognito_identity_pool" "orders_identity_pool" {
  identity_pool_name               = "orders-identity-pool"
  allow_unauthenticated_identities = false

  cognito_identity_providers {
    client_id               = aws_cognito_user_pool_client.paradise_cakes_client.id
    provider_name           = aws_cognito_user_pool.paradise_cakes_user_pool.endpoint
    server_side_token_check = false
  }
}

resource "aws_cognito_user_group" "paradise_cakes_admin_group" {
  name         = "paradise-cakes-admin-group"
  description  = "paradise cakes admin group"
  user_pool_id = aws_cognito_user_pool.paradise_cakes_user_pool.id
}

resource "aws_cognito_user_group" "paradise_cakes_user_group" {
  name         = "paradise-cakes-user-group"
  description  = "paradise cakes user group"
  user_pool_id = aws_cognito_user_pool.paradise_cakes_user_pool.id
}

