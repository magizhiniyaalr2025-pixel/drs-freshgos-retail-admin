from typing import List, Optional

from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    firstName:str
    lastName:str
    role:str  # Admin / Manager / Store Manager
    email: EmailStr
    password: str
    accessStores: Optional[List[str]] = []

class UserPartialUpdate(BaseModel):
    firstName: Optional[str]
    lastName: Optional[str]
    email: Optional[EmailStr]
    # password: Optional[str]
    # contactNumber: Optional[str]
    role: Optional[str]
    accessStores: Optional[List[str]]