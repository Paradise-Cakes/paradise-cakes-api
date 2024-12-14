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
    cleanup_cognito_users.append(response.json())
    response.raise_for_status()

    assert response.status_code == 201
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json().get("message") == "User created"
    assert response.json().get("UserConfirmed") == False


def test_post_v1_signup_username_exists_returns_400(
    request_helper, cleanup_cognito_users
):
    response_1 = request_helper.post(
        "/v1/signup",
        data={
            "email": "anthony.soprano@gmail.com",
            "password": "Password123$",
            "first_name": "Anthony",
            "last_name": "Soprano",
        },
    )
    response_1.raise_for_status()
    cleanup_cognito_users.append(response_1.json())

    response_2 = request_helper.post(
        "/v1/signup",
        data={
            "email": "anthony.soprano@gmail.com",
            "password": "Password123$",
            "first_name": "Anthony",
            "last_name": "Soprano",
        },
    )
    assert response_2.status_code == 400
    assert response_2.json().get("detail") == "User already exists with that email"


def test_post_v1_signup_invalid_password_returns_400(
    request_helper, cleanup_cognito_users
):
    response = request_helper.post(
        "/v1/signup",
        data={
            "email": "anthony.soprano@gmail.com",
            "password": "password",
            "first_name": "Anthony",
            "last_name": "Soprano",
        },
    )
    assert response.status_code == 400
    assert (
        response.json().get("detail")
        == "Password must have uppercase, lowercase, number, special character, and be at least 8 characters long"
    )
