from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from typing import List
from app.config.config import settings
from fastembed import TextEmbedding

_model = None

def _get_model():
    """Lazy-load the embedding model on first use, not at import time.
    Keeps startup memory low so the app fits in Render's free-tier RAM limit."""
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=settings.EMBEDDING_MODEL)
    return _model

def embed_chunks(chunks: List[str]):
    model = _get_model()
    return [vec.tolist() for vec in model.embed(chunks)]

def store_document_with_embeddings(db: Session, filename: str, chunks: List[str]):
    embeddings = embed_chunks(chunks)
    
    document = Document(filename=filename)
    db.add(document)
    db.flush()  

    for i, chunk_text in enumerate(chunks):
        db_chunk = DocumentChunk(
            content=chunk_text,
            embedding=embeddings[i],
            document_id=document.id
        )
        db.add(db_chunk)

    db.commit()
    db.refresh(document)
    return document