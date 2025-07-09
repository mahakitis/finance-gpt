from fastapi import FastAPI
from app.routers.upload import router as upload_document
from app.routers.query import router as query_router
from app.routers.session import router as sesion_router

app = FastAPI(title="FinanceGPT API")

# Include routers
app.include_router(upload_document)
app.include_router(query_router)
app.include_router(sesion_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to FinanceGPT API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}