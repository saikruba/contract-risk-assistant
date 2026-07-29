from fastapi import FastAPI
from app.api.v1.endpoints import contract
from app.core.config import settings

from app.core.database import Base, engine
from app.models.review_model import ContractReview

Base.metadata.create_all(bind=engine)


app = FastAPI(title=settings.APP_NAME)

app.include_router(contract.router, prefix="/api/v1")



