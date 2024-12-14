def test_post_v1_forgot_password_returns_200(
    request_helper, function_confirmed_account, cleanup_cognito_users
):
    email = function_confirmed_account["email"]

    response = request_helper.post(
        "/v1/forgot_password",
        data={
            "email": email,
        },
    )
    cleanup_cognito_users.append({"email": email})
    response.raise_for_status()

    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json().get("message") == f"Password reset email sent to {email}"
