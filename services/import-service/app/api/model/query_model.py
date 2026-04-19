from fastapi.params import Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class ImportFilter(BaseModel):
    store: Optional[str] = None
    status: Optional[List[str]] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    page: int = 1
    limit: int = 10