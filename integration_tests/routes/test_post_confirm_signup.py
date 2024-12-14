def test_post_v1_confirm_signup_returns_200(
    request_helper, function_signup_and_verification_code, cleanup_cognito_users
):
    email = function_signup_and_verification_code["email"]
    password = function_signup_and_verification_code["password"]
    confirmation_code = function_signup_and_verification_code["confirmation_code"]

    response = request_helper.post(
        "/v1/confirm_signup",
        data={
            "email": email,
            "password": password,
            "confirmation_code": confirmation_code,
        },
    )
    response.raise_for_status()
    cleanup_cognito_users.append(response.json())

    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json().get("message") == "User confirmed"
