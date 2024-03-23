resource "aws_cognitor_user_pool_client" "paradise_cakes_client" {
    name = "paradise-cakes-client"
    user_pool_id = aws_cognito_user_pool.paradise_cakes_user_pool.id

}

resource "aws_cognito_user_pool" "paradise_cakes_user_pool" {
    name = "paradise-cakes-user-pool"

    password_policy {
        minimum_length = 8
        require_lowercase = true
        require_numbers = true
        require_symbols = true
        require_uppercase = true
    }

    auto_verified_attributes = ["email"]

    mfa_configuration = "OPTIONAL"
    sms_authentication_message = "Your code is {####}"

    device_configuration {
        challenge_required_on_new_device = true
        device_only_remembered_on_user_prompt = true
    }

    email_configuration {
      email_sending_account = "COGNITO_DEFAULT"
    }

    account_recovery_setting {
        recovery_mechanism {
            name = "verified_email"
            priority = 1
        }
        recovery_mechanism {
            name = "verified_phone_number"
            priority = 2
        }
    }
}