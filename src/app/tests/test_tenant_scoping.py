# src/app/tests/test_tenant_scoping.py
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from jose import jwt
from datetime import datetime, timedelta
from app.core.config import settings

app = create_app()
client = TestClient(app)

def make_token(user_id, roles, hostel_id=None):
    exp = datetime.utcnow() + timedelta(minutes=15)
    data = {"sub": str(user_id), "roles": roles, "exp": exp}
    if hostel_id:
        data["hostel_id"] = hostel_id
    return jwt.encode(data, settings.JWT_SECRET, algorithm="HS256")

def test_tenant_can_only_see_their_own_invoices(monkeypatch):
    # Monkeypatch DB query to return fake invoices
    from app.models.tenant import Invoice
    fake_invoices = [
        Invoice(id=1, tenant_id=1, amount=100, currency="INR", status="paid"),
        Invoice(id=2, tenant_id=2, amount=200, currency="INR", status="pending"),
    ]
    async def fake_execute(query): return type("R", (), {"scalars": lambda self: fake_invoices})()
    monkeypatch.setattr("app.db.session.AsyncSession.execute", fake_execute)

    token = make_token(1, ["tenant"], hostel_id=1)
    headers = {"Authorization": f"Bearer {token}", "X-Hostel-ID": "1"}
    resp = client.get("/payments/invoices", headers=headers)
    assert resp.status_code == 200
    invoices = resp.json()
    assert all(inv["tenant_id"] == 1 for inv in invoices)

def test_tenant_blocked_from_other_hostel():
    token = make_token(1, ["tenant"], hostel_id=1)
    headers = {"Authorization": f"Bearer {token}", "X-Hostel-ID": "2"}  # mismatch
    resp = client.get("/payments/invoices", headers=headers)
    assert resp.status_code == 403

def test_hostel_admin_and_super_admin_still_work():
    token_admin = make_token(2, ["hostel_admin"], hostel_id=2)
    headers_admin = {"Authorization": f"Bearer {token_admin}", "X-Hostel-ID": "2"}
    resp_admin = client.get("/rooms", headers=headers_admin)
    assert resp_admin.status_code != 403

    token_super = make_token(99, ["super_admin"])
    headers_super = {"Authorization": f"Bearer {token_super}", "X-Hostel-ID": "123"}
    resp_super = client.get("/rooms", headers=headers_super)
    assert resp_super.status_code != 403
