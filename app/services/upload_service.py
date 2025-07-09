from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.services.chunker import chunk_paragraphs
from app.services.embeddings import store_document_with_embeddings
import fitz  # PyMuPDF

def process_uploaded_document(file: UploadFile, db: Session):
    filename = file.filename.lower()
    
    if not (filename.endswith(".txt") or filename.endswith(".pdf")):
        raise ValueError("Only .txt and .pdf files are supported")

    if filename.endswith(".txt"):
        content = file.file.read()
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError("Unable to decode .txt file. Ensure it is UTF-8 encoded.")

    elif filename.endswith(".pdf"):
        try:
            with fitz.open(stream=file.file.read(), filetype="pdf") as doc:
                text = "\n".join([page.get_text() for page in doc])
        except Exception as e:
            raise RuntimeError(f"Failed to read PDF: {str(e)}")

    chunks = chunk_paragraphs(text)
    document = store_document_with_embeddings(db, file.filename, chunks)
    return document
