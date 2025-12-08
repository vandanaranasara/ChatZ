# backend/models.py
from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import declarative_base
from backend.database import Base

class FileInfo(Base):
    __tablename__ = "file_info"

    file_id = Column(String, primary_key=True)
    file_name = Column(String, unique=True, nullable=True)
    num_pages = Column(Integer, nullable=True)
    uploaded_at = Column(String, nullable=True)
    embedding_status = Column(Boolean, default=False)
    
    
