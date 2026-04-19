from datetime import date
import string
from typing import List

from fastapi import APIRouter, Form, Query, UploadFile, File, Depends, Body
from app.utils.excel_parser import ExcelParser
from app.services.import_service import ImportService
from app.core.security import get_current_user
from app.api.model.query_model import ImportFilter
from common.responses.base import success_response
from typing import List, Optional
from fastapi.exceptions import HTTPException

router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    store: str = Form(...),
    user=Depends(get_current_user)
):
    contents = await file.read()
    parser = ExcelParser()

    # Parse Excel
    records = await parser.parse_excel(contents)
    # Save to DB
    service = ImportService()
    data = await service.save_data(records, user,store)
    return success_response(
        data,
        message="File processed successfully"
    )

@router.put("/update/{id}")
async def update(
    id: str, 
    data: dict,
    user=Depends(get_current_user)):
    service = ImportService()
    result = await service.update_data(id, data)
    return success_response(
        result
    )

@router.get("/get/{id}")
async def get(
    id: str, 
    user=Depends(get_current_user)):
    service = ImportService()
    print(id)
    result = await service.get(id)
    return success_response(
        result
    )

@router.get("/list/")
async def list(
    status: Optional[List[str]] = Query(None),
    store: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = 1,
    limit: int = 30,
    user=Depends(get_current_user)
):
    filter = ImportFilter(
        status=status,
        store=store,
        from_date=from_date,
        to_date=to_date,
        page=page,
        limit=limit,
    )

    service = ImportService()
    result = await service.list(filter)

    return success_response(result)

@router.post("/approve")
async def approve(
    data: dict = Body(...),
    user=Depends(get_current_user)
):
    id = data.get("id")
    comment = data.get("comment")

    if not id or not comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both 'id' and 'comment' are required."
        )

    service = ImportService()

    # Update the document status to 'approved' and add the comment
    result = await service.approve_data(id, comment, user)

    return success_response(
        result,
        message="Document approved successfully"
    )
