from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session  
from app.schemas.query_schema import QueryRequest, QueryResponse
from app.services.query_service import process_query
from app.db_utils.database import get_db 

router = APIRouter(prefix="/query", tags=["Query"])

@router.post("", response_model=QueryResponse)
def handle_query(payload: QueryRequest, db: Session = Depends(get_db)):
    return process_query(payload, db)
