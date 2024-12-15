def test_post_v1_confirm_forgot_password_returns_200(
    request_helper, function_forgot_password_code
):
    email = function_forgot_password_code["email"]
    reset_code = function_forgot_password_code["reset_code"]

    response = request_helper.post(
        "/v1/confirm_forgot_password",
        data={
            "email": email,
            "code": reset_code,
            "password": "3r@fv3sagv#",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json().get("message") == f"Password reset for {email} successful"
