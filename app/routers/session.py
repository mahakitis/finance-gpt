from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid
from app.db_utils.database import get_db
from app.models.chatsession import ChatSession

router = APIRouter(prefix="/session", tags=["Session"])

@router.post("/create")
def create_session(db: Session = Depends(get_db)):
    session_id = str(uuid.uuid4())
    session = ChatSession(session_id=session_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"session_id": session.session_id}
