import logging
from common.request.context import get_trace_id

def setup_logger():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

class ContextLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def info(self, msg):
        self.logger.info(self._format(msg))

    def error(self, msg):
        self.logger.error(self._format(msg))

    def _format(self, msg):
        return {
            "trace_id": get_trace_id(),
            "message": msg
        }
