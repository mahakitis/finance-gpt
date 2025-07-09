from pydantic import BaseModel
from typing import List
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str

class DocumentCreate(DocumentBase):
    pass

class DocumentChunkBase(BaseModel):
    content: str

class DocumentChunkCreate(DocumentChunkBase):
    pass

class DocumentChunkOut(DocumentChunkBase):
    id: int
    document_id: int
    
    class Config:
        from_attributes = True

class DocumentOut(DocumentBase):
    id: int
    uploaded_at: datetime
    chunks: List[DocumentChunkOut] = []

    class Config:
        from_attributes = True
