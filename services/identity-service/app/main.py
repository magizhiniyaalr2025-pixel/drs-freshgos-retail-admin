from fastapi import FastAPI
from app.route import auth, users,store

from common.middleware.request_middleware import RequestMiddleware
from common.logger.logger import setup_logger
from common.exceptions.handler import global_exception_handler
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Identity Service (MongoDB)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

setup_logger()

app.add_middleware(RequestMiddleware)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(auth.router, prefix="/auth")
app.include_router(users.router, prefix="/users")
app.include_router(store.router, prefix="/store")
