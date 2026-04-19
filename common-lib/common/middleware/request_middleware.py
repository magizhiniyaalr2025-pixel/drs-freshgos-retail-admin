from starlette.middleware.base import BaseHTTPMiddleware
from common.request.context import set_trace_id, get_trace_id
import time

class RequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        trace_id = set_trace_id()
        start = time.time()

        response = await call_next(request)

        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Process-Time"] = str(time.time() - start)

        return response
