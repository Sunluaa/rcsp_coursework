from tests.conftest import auth_headers


def test_login_and_get_current_user(client):
    headers = auth_headers(client, "admin")
    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@example.com"
    assert data["role"]["name"] == "admin"


def test_invalid_login_rejected(client):
    response = client.post(
        "/api/auth/login", json={"email": "admin@example.com", "password": "Wrong12345!"}
    )

    assert response.status_code == 401


def test_local_demo_email_reaches_auth_logic(client):
    response = client.post(
        "/api/auth/login", json={"email": "editor@knowledgebaza.local", "password": "Editor12345!"}
    )

    assert response.status_code == 401


def test_admin_can_create_user(client):
    headers = auth_headers(client, "admin")
    response = client.post(
        "/api/users",
        headers=headers,
        json={
            "email": "new.employee@example.com",
            "password": "Employee12345!",
            "full_name": "New Employee",
            "role_name": "employee",
        },
    )

    assert response.status_code == 201, response.text
    assert response.json()["role"]["name"] == "employee"


def test_non_admin_cannot_create_user(client):
    headers = auth_headers(client, "editor")
    response = client.post(
        "/api/users",
        headers=headers,
        json={
            "email": "blocked@example.com",
            "password": "Employee12345!",
            "full_name": "Blocked User",
            "role_name": "employee",
        },
    )

    assert response.status_code == 403


def test_invalid_jwt_rejected(client):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token"})

    assert response.status_code == 401


def test_nonexistent_role_rejected(client):
    headers = auth_headers(client, "admin")
    response = client.post(
        "/api/users",
        headers=headers,
        json={
            "email": "ghost@example.com",
            "password": "Employee12345!",
            "full_name": "Ghost Role",
            "role_name": "manager",
        },
    )

    assert response.status_code in {400, 422}
