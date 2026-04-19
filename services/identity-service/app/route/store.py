# app/routes/store_route.py
from fastapi import APIRouter
from app.services.store_service import StoreService
from app.repositories.store_repo import StoreRepository
from app.schemas.store_schema import StoreCreate, StoreUpdate, StorePartialUpdate
from common.responses.base import success_response

router = APIRouter()
service = StoreService(StoreRepository())

@router.post("/")
async def create_store(data: StoreCreate):
    store = await service.create_store(data)
    return success_response(data=store, message="Store created")

@router.get("/")
async def list_stores():
    stores = await service.list_stores()
    return success_response(data=stores, message=f"{len(stores)} stores found")

@router.get("/{store_id}")
async def get_store(store_id: str):
    store = await service.get_store(store_id)
    return success_response(data=store, message="Store fetched successfully")

@router.put("/{store_id}")
async def update_store(store_id: str, data: StoreUpdate):
    updated = await service.update_store(store_id, data)
    return success_response(data=updated, message="Store updated successfully")

@router.patch("/{store_id}")
async def partial_update_store(store_id: str, data: StorePartialUpdate):
    updated = await service.partial_update_store(store_id, data.dict(exclude_unset=True))
    return success_response(data=updated, message="Store partially updated successfully")

@router.delete("/{store_id}")
async def delete_store(store_id: str):
    await service.delete_store(store_id)
    return success_response(data={"deleted": True}, message="Store deleted successfully")
