import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-with-enough-length-for-jwt"
os.environ["BCRYPT_ROUNDS"] = "4"
os.environ["CORS_ORIGINS"] = ""
os.environ["STORAGE_PROVIDER"] = "local"
os.environ["LOCAL_STORAGE_PATH"] = "uploads/test"
os.environ["MAX_UPLOAD_SIZE_BYTES"] = "1024"

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine, get_db
from app.core.security import get_password_hash
from app.main import app
from app.models import Role, User
from app.storage.factory import get_storage_service


TEST_USERS = {
    "admin": ("admin@example.com", "Admin12345!"),
    "editor": ("editor@example.com", "Editor12345!"),
    "employee": ("employee@example.com", "Employee12345!"),
}


def seed_roles_and_users(db):
    roles = {
        "admin": Role(name="admin", description="Admin"),
        "editor": Role(name="editor", description="Editor"),
        "employee": Role(name="employee", description="Employee"),
    }
    db.add_all(roles.values())
    db.flush()
    for role_name, (email, password) in TEST_USERS.items():
        db.add(
            User(
                email=email,
                password_hash=get_password_hash(password),
                full_name=f"{role_name.title()} User",
                role=roles[role_name],
                is_active=True,
            )
        )
    db.commit()


@pytest.fixture()
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_roles_and_users(db)
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        get_storage_service.cache_clear()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def login(client: TestClient, role: str) -> str:
    email, password = TEST_USERS[role]
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_headers(client: TestClient, role: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {login(client, role)}"}


def create_category(client: TestClient, headers: dict[str, str], name: str = "Policies") -> int:
    response = client.post("/api/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def create_tag(client: TestClient, headers: dict[str, str], name: str = "Important") -> int:
    response = client.post("/api/tags", headers=headers, json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()["id"]
