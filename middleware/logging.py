import time
import uuid
from typing import Optional, Any
from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
logger.remove()
logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    serialize=True
)
logger.add(
    "logs/error.log",
    rotation="500 MB",
    retention="10 days",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    serialize=True
)
def get_correlation_id(request: Request) -> str:
    return getattr(request.state, "correlation_id", "unknown")
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        start_time = time.time()
        client_host = request.client.host if request.client else None
        logger.bind(
            correlation_id=correlation_id,
            method=request.method,
            url=str(request.url),
            path=request.url.path,
            query_params=str(request.query_params),
            client_ip=client_host,
            user_agent=request.headers.get("user-agent"),
        ).info("Request started")
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.bind(
                correlation_id=correlation_id,
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                process_time_seconds=round(process_time, 4),
            ).info("Request completed")
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Process-Time"] = str(round(process_time, 4))
            return response
        except Exception as exc:
            process_time = time.time() - start_time
            logger.bind(
                correlation_id=correlation_id,
                method=request.method,
                url=str(request.url),
                process_time_seconds=round(process_time, 4),
                exception_type=type(exc).__name__,
                exception_message=str(exc),
            ).error("Request failed")
            raise