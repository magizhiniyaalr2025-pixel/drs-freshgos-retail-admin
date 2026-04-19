# app/schemas/store_schema.py
from pydantic import BaseModel
from typing import Optional

class StoreCreate(BaseModel):
    name: str
    address: str

class StoreUpdate(BaseModel):
    name: str
    address: str

class StorePartialUpdate(BaseModel):
    name: Optional[str]
    address: Optional[str]
