from fastapi import FastAPI, UploadFile

app = FastAPI()

@app.post("/upload-contract")
async def upload_contract(file: UploadFile | None = None):
    if not file:
        return {"message": "No file uploaded"}

    return {
        "filename": file.filename,
        "risk": "low",
        "issues": ["missing clause"]
    }
