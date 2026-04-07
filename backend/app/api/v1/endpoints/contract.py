from fastapi import APIRouter, UploadFile
from app.services.contract_service import analyze_contract

router = APIRouter()

@router.post("/upload-contract")
async def upload_contract(file: UploadFile | None = None):
    if not file:
        return {"message": "No file uploaded"}

    # Here we use the service
    result = analyze_contract(file.filename)
    return result.dict()
