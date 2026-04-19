from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]

import_collection = db["imports"]
scratch_card_issue_collection = db["scratch_card_issue"]

