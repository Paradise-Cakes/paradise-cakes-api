def test_post_v1_signup_returns_201(request_helper, cleanup_cognito_users):
    response = request_helper.post(
        "/v1/signup",
        data={
            "email": "anthony.soprano@gmail.com",
            "password": "Password123$",
            "first_name": "Anthony",
            "last_name": "Soprano",
        },
    )
    response.raise_for_status()
    cleanup_cognito_users.append(response.json())

    assert response.status_code == 201
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json().get("message") == "User created"
    assert response.json().get("UserConfirmed") == False
