from fastapi import APIRouter, HTTPException
from app.services.user_service import UserService
from app.repositories.user_repo import UserRepository
from app.schemas.user_schema import UserCreate, UserPartialUpdate
from common.responses.base import success_response

router = APIRouter()
service = UserService(UserRepository())

@router.post("/")
async def create_user(data: UserCreate):
    user = await service.create_user(data)
    return success_response(
        data={"email": user["email"]},
        message="User created"
    )

@router.get("/")
async def list_users():
    users = await service.list_users()
    return success_response(
        data=users,
        message=f"{len(users)} users found"
    )

@router.get("/{user_id}")
async def get_user(user_id: str):
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(
        data=user,
        message="User fetched successfully"
    )

@router.put("/{user_id}")
async def update_user(user_id: str, data: UserPartialUpdate):
    updated_user = await service.update_user(user_id, data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(
        data=updated_user,
        message="User updated successfully"
    )

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(
        data={"deleted": True},
        message="User deleted successfully"
    )

