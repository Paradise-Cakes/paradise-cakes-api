def test_post_v1_signup_returns_201(request_helper, cleanup_cognito_users):
    response = request_helper.post(
        "/v1/signup",
        body={
            "email": "anthony.soprano@gmail.com",
            "password": "password123",
            "first_name": "Anthony",
            "last_name": "Soprano",
        },
    )
    response.raise_for_status()
    cleanup_cognito_users.append(response.json())

    assert response.status_code == 201
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json() == {
        "message": "User created",
        "email": "anthony.soprano@gmail.com",
        "given_name": "Anthony",
        "family_name": "Soprano",
        "UserConfirmed": False,
        "UserSub": response.json().get("UserSub"),
    }
