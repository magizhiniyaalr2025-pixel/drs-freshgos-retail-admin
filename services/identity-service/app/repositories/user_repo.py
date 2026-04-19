
from app.core.security import hash_password
from bson import ObjectId

from app.db.mongo import user_collection

class UserRepository:

    async def get_by_email(self, email):
        return await user_collection.find_one({"email": email})

    async def create(self, user):
        existing = await user_collection.find_one({"email": user["email"]})
        if existing:
            raise ValueError("Email already exists")

        # Hash the password
        user["password"] = hash_password(user["password"])

        # Insert user into DB
        result = await user_collection.insert_one(user)
        user["_id"] = str(result.inserted_id)

        # Optionally remove password before returning
        user.pop("password", None)

        return user
    
    async def list(self):
        users = []
        async for user in user_collection.find():
            user["_id"] = str(user["_id"])
            users.append(user)
        return users

    # 🔹 Get single user by ID
    async def get(self, user_id: str):
        user = await user_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
        return user

    # 🔹 Edit / Update user
    async def edit(self, user_id: str, user_data: dict):
        if "email" in user_data:
            existing = await user_collection.find_one({"email": user_data["email"], "_id": {"$ne": ObjectId(user_id)}})
            if existing:
                raise ValueError("Email already exists")

        result = await user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": user_data}
        )
        if result.matched_count == 0:
            return None
        return await self.get(user_id)

    # 🔹 Delete user by ID
    async def delete(self, user_id: str):
        result = await user_collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

