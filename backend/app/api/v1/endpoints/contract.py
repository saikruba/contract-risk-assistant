from fastapi import APIRouter, UploadFile, File
from app.services.contract_service import analyze_contract

router = APIRouter()

@router.post("/upload-contract")
async def upload_contract(file: UploadFile = File(...)):
    return analyze_contract(file.filename)
