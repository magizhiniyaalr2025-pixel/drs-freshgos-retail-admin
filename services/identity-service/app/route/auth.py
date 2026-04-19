from fastapi import APIRouter, Response
from app.services.auth_service import AuthService
from app.repositories.user_repo import UserRepository
from common.responses.base import success_response

router = APIRouter()

@router.post("/login")
async def login(data: dict, response: Response):
    service = AuthService(UserRepository())
    token = await service.login(data["email"], data["password"])
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
        domain="localhost"
    )
    return success_response(
        data={"token": token},
        message="Login successful"
    )
