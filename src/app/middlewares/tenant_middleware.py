# src/app/middlewares/tenant_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from typing import Optional


class TenantResolverMiddleware(BaseHTTPMiddleware):
    """
    Resolve tenant from header X-Hostel-ID (preferred) or query param `hostel_id`.
    Attaches `request.state.tenant_schema` = 'hostel_{id}' or None.
    """

    async def dispatch(self, request: Request, call_next):
        hostel_id: Optional[str] = None
        # header preferred
        if "x-hostel-id" in request.headers:
            hostel_id = request.headers.get("x-hostel-id")
        else:
            # fallback to query param
            qs_val = request.query_params.get("hostel_id")
            if qs_val:
                hostel_id = qs_val

        if hostel_id:
            # Basic sanitation: only digits expected - adjust as needed
            hostel_id = hostel_id.strip()
            # safe schema name
            request.state.tenant_schema = f"hostel_{hostel_id}"
        else:
            request.state.tenant_schema = None

        response = await call_next(request)
        return response
