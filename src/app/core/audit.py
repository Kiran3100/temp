from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import datetime
import json

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        now = datetime.datetime.utcnow()
        response = await call_next(request)
        # store audit: you can push to DB or queue
        audit = {
            "path": request.url.path,
            "method": request.method,
            "user": getattr(request.state, "user", None),
            "status_code": response.status_code,
            "timestamp": now.isoformat(),
        }
        # For demo: print; in prod push to DB table audit_logs or to a structured log system
        print("AUDIT", json.dumps(audit))
        return response
