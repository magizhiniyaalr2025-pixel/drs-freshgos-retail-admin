from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]

user_collection = db["users"]

store_collection = db["store"]