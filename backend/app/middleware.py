"""
AEGIS Security & Tracing Middleware
Conforms to PRD 2: E-009 Structured error reporting, request correlation ID tracing,
and security headers.
"""
import uuid
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("aegis.middleware")


class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """
    Attaches a unique X-Correlation-ID to every incoming HTTP request and response header.
    Tracks request latency without leaking sensitive internal details.
    """
    async def dispatch(self, request: Request, call_next):
        # Read incoming correlation ID or generate a new one
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        start_time = time.time()
        response: Response = await call_next(request)
        process_time_ms = (time.time() - start_time) * 1000

        # Attach tracking and security headers
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Response-Time-Ms"] = f"{process_time_ms:.2f}"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"

        return response
