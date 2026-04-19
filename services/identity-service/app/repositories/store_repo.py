# app/repositories/store_repo.py
from app.db.mongo import store_collection
from bson import ObjectId

class StoreRepository:

    # Create
    async def create(self, store: dict):
        existing = await store_collection.find_one({"name": store["name"]})
        if existing:
            raise ValueError("Store name already exists")
        result = await store_collection.insert_one(store)
        store["_id"] = str(result.inserted_id)
        return store

    # List all
    async def list(self):
        stores = []
        async for store in store_collection.find():
            store["_id"] = str(store["_id"])
            stores.append(store)
        return stores

    # Get single
    async def get(self, store_id: str):
        store = await store_collection.find_one({"_id": ObjectId(store_id)})
        if store:
            store["_id"] = str(store["_id"])
        return store

    # Edit / Update (full)
    async def edit(self, store_id: str, store_data: dict):
        if "name" in store_data:
            existing = await store_collection.find_one({"name": store_data["name"], "_id": {"$ne": ObjectId(store_id)}})
            if existing:
                raise ValueError("Store name already exists")
        result = await store_collection.update_one(
            {"_id": ObjectId(store_id)},
            {"$set": store_data}
        )
        if result.matched_count == 0:
            return None
        return await self.get(store_id)

    # Partial update
    async def edit_partial(self, store_id: str, store_data: dict):
        return await self.edit(store_id, store_data)

    # Delete
    async def delete(self, store_id: str):
        result = await store_collection.delete_one({"_id": ObjectId(store_id)})
        return result.deleted_count > 0
