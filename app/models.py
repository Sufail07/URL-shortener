from .database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

class URL(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)


