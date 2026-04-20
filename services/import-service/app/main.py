from fastapi import FastAPI
from app.api import import_api
from app.api import report_api

from common.middleware.request_middleware import RequestMiddleware
from common.logger.logger import setup_logger
from common.exceptions.handler import global_exception_handler
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Import Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nextjs-app-356841010934.asia-south1.run.app",
        'http://localhost:3000' # frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
setup_logger()

app.add_middleware(RequestMiddleware)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(import_api.router, prefix="/import")
app.include_router(report_api.router, prefix="/report")
