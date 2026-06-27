from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class ContractReview(Base):

    __tablename__ = "contract_reviews"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String)

    summary = Column(Text)

    issues = Column(Text)


