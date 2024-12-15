def test_post_v1_resend_confirmation_code_returns_200(request_helper, function_signup):
    email = function_signup["email"]

    response = request_helper.post(
        "/v1/resend_confirmation_code",
        data={
            "email": email,
        },
    )
    response.raise_for_status()

    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json().get("message") == "Confirmation code resent"


def test_post_v1_resend_confirmation_code_user_not_found_returns_400(request_helper):
    email = "wut@gmail.com"

    response = request_helper.post(
        "/v1/resend_confirmation_code",
        data={
            "email": email,
        },
    )

    assert response.status_code == 400
    assert response.json().get("detail") == "User not found"
