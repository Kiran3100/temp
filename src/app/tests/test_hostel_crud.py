import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_create_hostel_super_admin_token(monkeypatch):
    # create stub token with super_admin role
    token = "test-super-token"
    monkeypatch.setattr("app.middlewares.rbac.verify_token", lambda t: {"sub":"1","roles":["super_admin"]})
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post("/hostels/", json={"name": "Test Hostel"}, headers=headers)
    assert resp.status_code in (200, 201)
