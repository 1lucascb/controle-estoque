from fastapi.testclient import TestClient
from src.api.main import app
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
