from fastapi import APIRouter, UploadFile, File, Depends
from app.utils.excel_parser import ExcelParser
from app.services.import_service import ImportService
from app.core.security import get_current_user
from app.services.report_service import ReportService

from common.responses.base import success_response

router = APIRouter()


@router.post("/summary/")
async def report_summary(
    filters: dict,
    user=Depends(get_current_user)):
    service = ReportService()
    result = await service.get_summary(filters)
    return success_response(
        data=result,
        message="Report fetched successfully"
    )
