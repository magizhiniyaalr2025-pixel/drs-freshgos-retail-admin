def success_response(data=None, message="Success", trace_id=None):
    return {
        "success": True,
        "message": message,
        "data": data,
        "error": None,
        "trace_id": trace_id
    }

def error_response(message="Error", error=None, trace_id=None):
    return {
        "success": False,
        "message": message,
        "data": None,
        "error": error,
        "trace_id": trace_id
    }
