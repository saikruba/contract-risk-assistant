from fastapi import APIRouter, UploadFile, File
import os
from app.services.contract_service import analyze_contract

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-contract")
async def upload_contract(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save uploaded PDF
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Pass file path to service
    return analyze_contract(file_path)
