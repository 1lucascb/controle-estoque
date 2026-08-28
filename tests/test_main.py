import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from src.api.main import app
from src.api.infrastructure.models import User
from src.api.schemas.schemas import ChangePasswordRequest
from src.api.services.user_service import UserService
from src.api.utils.hash import HashUtils
from src.api.utils.jwt_handler import create_access_token

client = TestClient(app)

def test_protected_route_requires_access_token_cookie():
    response = client.get("/api/v1/health")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_protected_route_rejects_invalid_access_token_cookie():
    response = client.get("/api/v1/health", cookies={"access_token": "invalid-token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_protected_route_accepts_raw_access_token_cookie():
    token = create_access_token({"user_id": 1, "role": "admin", "username": "admin"})
    response = client.get("/api/v1/health", cookies={"access_token": token})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_products_endpoint():
    token = create_access_token({"user_id": 1, "role": "admin", "username": "admin"})
    response = client.get("/api/v1/products", cookies={"access_token": token})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_change_password_requires_access_token_cookie():
    response = client.post("/api/v1/auth/change-password", json={
        "current_password": "old-password",
        "new_password": "new-password",
        "confirm_password": "new-password",
    })
    assert response.status_code == 401


def test_change_password_schema_rejects_short_or_mismatched_passwords():
    with pytest.raises(ValidationError):
        ChangePasswordRequest(
            current_password="old-password",
            new_password="short",
            confirm_password="short",
        )

    with pytest.raises(ValidationError):
        ChangePasswordRequest(
            current_password="old-password",
            new_password="new-password",
            confirm_password="different-password",
        )


def test_change_password_updates_hash_without_external_user_id():
    user = User(id=7, password_hash=HashUtils.generate_pwd("old-password"), is_active=True)
    service = UserService(db=type("Database", (), {"commit": lambda self: None})())
    service.get_user_by_id = lambda user_id: user if user_id == 7 else None

    changed = service.change_password(
        7,
        ChangePasswordRequest(
            current_password="old-password",
            new_password="new-password",
            confirm_password="new-password",
        ),
    )

    assert changed is True
    assert HashUtils.check_pwd("new-password", user.password_hash)
    assert not HashUtils.check_pwd("old-password", user.password_hash)
