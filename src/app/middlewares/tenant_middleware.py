from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from typing import Optional


class TenantResolverMiddleware(BaseHTTPMiddleware):
    """
    Resolve tenant from header `X-Hostel-ID` (preferred) or query param `hostel_id`.
    Attaches `request.state.tenant_schema` = 'hostel_{id}' or None.
    """

    async def dispatch(self, request: Request, call_next):
        hostel_id: Optional[str] = (
            request.headers.get("X-Hostel-ID")
            or request.query_params.get("hostel_id")
        )

        if hostel_id:
            hostel_id = hostel_id.strip()
            # sanitize: only digits allowed
            if not hostel_id.isdigit():
                request.state.tenant_schema = None
            else:
                request.state.tenant_schema = f"hostel_{hostel_id}"
        else:
            request.state.tenant_schema = None

        response = await call_next(request)
        return response
