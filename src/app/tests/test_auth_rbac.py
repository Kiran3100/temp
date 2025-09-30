# src/app/tests/test_auth_rbac.py
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.services import auth_service
from app.core.security import create_access_token
from app.schemas.user import Role

app = create_app()
client = TestClient(app)


# Simple in-memory user store for tests
_FAKE_USERS = {}
class FakeUser:
    def __init__(self, id, email, hashed_password, roles):
        self.id = id
        self.email = email
        self.hashed_password = hashed_password
        self.roles = roles

@pytest.fixture(autouse=True)
def patch_auth(monkeypatch):
    # monkeypatch create_user to insert into _FAKE_USERS
    async def fake_create_user(db, email, password, full_name=None, roles=None):
        user_id = len(_FAKE_USERS) + 1
        hashed = auth_service.get_password_hash(password) if hasattr(auth_service, "get_password_hash") else None
        # But our service uses core.security.get_password_hash; call that
        from app.core.security import get_password_hash
        hashed = get_password_hash(password)
        u = FakeUser(id=user_id, email=email, hashed_password=hashed, roles=roles or [Role.tenant.value])
        _FAKE_USERS[email] = u
        return u

    async def fake_authenticate_user(db, email, password):
        u = _FAKE_USERS.get(email)
        if not u:
            return None
        # verify using core.security.verify_password
        from app.core.security import verify_password
        if not verify_password(password, u.hashed_password):
            return None
        return u

    # Ensure create_token_for_user uses actual create_access_token from core.security
    monkeypatch.setattr(auth_service, "create_user", fake_create_user)
    monkeypatch.setattr(auth_service, "authenticate_user", fake_authenticate_user)
    yield
    _FAKE_USERS.clear()


def test_register_and_login_and_protected_route_access():
    # register a super_admin
    register_payload = {
        "email": "super@example.com",
        "password": "superpass",
        "full_name": "Super",
        "roles": [Role.super_admin.value]
    }
    resp = client.post("/auth/register", json=register_payload)
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token

    # Use token to call protected create_hostel endpoint (requires super_admin)
    headers = {"Authorization": f"Bearer {token}"}
    create_resp = client.post("/hostels", json={"name": "T1"}, headers=headers)
    # For this test the route will attempt to write to DB; in case DB not available, we accept both 200 and 500,
    # but the key is that auth allowed the request (i.e., not 403)
    assert create_resp.status_code != 403

    # register a tenant (non-admin)
    tenant_payload = {
        "email": "tenant@example.com",
        "password": "tenantpass",
        "full_name": "Tenant",
        "roles": [Role.tenant.value]
    }
    r2 = client.post("/auth/register", json=tenant_payload)
    assert r2.status_code == 200
    tenant_token = r2.json()["access_token"]
    assert tenant_token

    # tenant tries to create hostel -> should be forbidden (403)
    headers2 = {"Authorization": f"Bearer {tenant_token}"}
    create_resp2 = client.post("/hostels", json={"name": "T2"}, headers=headers2)
    assert create_resp2.status_code == 403
