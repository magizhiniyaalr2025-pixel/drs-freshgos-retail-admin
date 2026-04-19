from fastapi.responses import JSONResponse
from common.responses.base import error_response
from common.request.context import get_trace_id

def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=error_response(
            message="Internal Server Error",
            error=str(exc),
            trace_id=get_trace_id()
        )
    )
