import uuid
from contextvars import ContextVar

trace_id_ctx = ContextVar("trace_id", default=None)

def set_trace_id():
    trace_id = str(uuid.uuid4())
    trace_id_ctx.set(trace_id)
    return trace_id

def get_trace_id():
    return trace_id_ctx.get()
