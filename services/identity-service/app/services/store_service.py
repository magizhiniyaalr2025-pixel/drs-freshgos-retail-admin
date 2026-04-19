# app/services/store_service.py
from fastapi import HTTPException

class StoreService:
    def __init__(self, repo):
        self.repo = repo

    async def create_store(self, data):
        try:
            return await self.repo.create(data.dict())
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def list_stores(self):
        return await self.repo.list()

    async def get_store(self, store_id):
        store = await self.repo.get(store_id)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        return store

    async def update_store(self, store_id, data):
        try:
            updated = await self.repo.edit(store_id, data.dict())
            if not updated:
                raise HTTPException(status_code=404, detail="Store not found")
            return updated
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def partial_update_store(self, store_id, data):
        return await self.update_store(store_id, data)

    async def delete_store(self, store_id):
        deleted = await self.repo.delete(store_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Store not found")
        return deleted
