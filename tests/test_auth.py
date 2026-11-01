from models import User


def test_register_and_password_is_hashed(client, app):

    response = client.post(
        "/api/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201

    with app.app_context():

        user = User.query.filter_by(
            username="alice"
        ).first()

        assert user is not None
        assert user.password_hash != "password123"
        assert user.check_password("password123")


def test_duplicate_username_rejected(client):

    payload = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "password123"
    }

    assert client.post(
        "/api/auth/register",
        json=payload
    ).status_code == 201

    payload["email"] = "another@example.com"

    assert client.post(
        "/api/auth/register",
        json=payload
    ).status_code == 409


def test_login_logout_and_me(client):

    client.post(
        "/api/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123"
        }
    )

    assert client.get(
        "/api/auth/me"
    ).status_code == 200

    client.delete("/api/auth/logout")

    assert client.get(
        "/api/auth/me"
    ).status_code == 401

    response = client.post(
        "/api/auth/login",
        json={
            "username": "alice",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    assert client.get(
        "/api/auth/me"
    ).status_code == 200


def test_bad_login_is_unauthorized(client):

    response = client.post(
        "/api/auth/login",
        json={
            "username": "missing",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def test_weak_password_rejected(client):

    response = client.post(
        "/api/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "123"
        }
    )

    assert response.status_code == 400