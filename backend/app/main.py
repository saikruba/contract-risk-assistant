from fastapi import FastAPI
from app.api.v1.endpoints import contract
from app.core.config import settings

# ✅ Ensure LLM initializes
from app.services import llm_service  

app = FastAPI(title=settings.APP_NAME)

app.include_router(contract.router, prefix="/api/v1")
