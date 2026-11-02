import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory sliding window rate limiter per client IP."""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.ip_history: dict[str, list[float]] = defaultdict(list)
        self._last_cleanup = time.time()

    def _cleanup_stale_records(self, now: float) -> None:
        """Prunes historical IP records older than 120 seconds to prevent unbounded memory growth."""
        if now - self._last_cleanup > 60.0:
            stale_threshold = now - 60.0
            keys_to_delete = []
            for ip, timestamps in self.ip_history.items():
                active = [t for t in timestamps if t > stale_threshold]
                if active:
                    self.ip_history[ip] = active
                else:
                    keys_to_delete.append(ip)
            for ip in keys_to_delete:
                del self.ip_history[ip]
            self._last_cleanup = now

    async def dispatch(self, request: Request, call_next):
        if self.requests_per_minute <= 0 or not request.url.path.startswith("/api/"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        self._cleanup_stale_records(now)

        window_start = now - 60.0
        timestamps = [t for t in self.ip_history[client_ip] if t > window_start]

        if len(timestamps) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
                headers={"Retry-After": "60"},
            )

        timestamps.append(now)
        self.ip_history[client_ip] = timestamps

        return await call_next(request)
