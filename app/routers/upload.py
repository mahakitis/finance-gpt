from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.upload_service import process_uploaded_document
import app.schemas.document_schema as schemas
from app.db_utils.database import get_db

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/document", response_model=schemas.DocumentOut)
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        return process_uploaded_document(file, db)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
