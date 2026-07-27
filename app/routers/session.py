from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
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

@router.get("/{session_id}/history")
def get_session_history(session_id: str, db: Session = Depends(get_db)):
    """Return past question/answer turns for a session, oldest first."""
    exists = db.execute(
        text("SELECT 1 FROM chat_sessions WHERE session_id = :sid"),
        {"sid": session_id},
    ).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Session not found")

    rows = db.execute(
        text("""
            SELECT question, answer, created_at
            FROM memory_nodes
            WHERE session_id = :sid
            ORDER BY created_at
        """),
        {"sid": session_id},
    )
    return {
        "session_id": session_id,
        "history": [
            {"question": r.question, "answer": r.answer, "created_at": r.created_at}
            for r in rows
        ],
    }