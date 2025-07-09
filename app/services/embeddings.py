from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from typing import List
from app.config.config import settings
from sentence_transformers import SentenceTransformer  

model = SentenceTransformer(settings.EMBEDDING_MODEL)

def embed_chunks(chunks: List[str]):
    return model.encode(chunks).tolist()

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
