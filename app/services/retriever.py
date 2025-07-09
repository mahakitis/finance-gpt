from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from app.config.config import settings
from app.db_utils.database import engine

model = SentenceTransformer(settings.EMBEDDING_MODEL)

def search_pgvector(query: str, top_k=5) -> list[dict]:
    query_vec = model.encode([query])[0].tolist()
    sql = text(f"""
    SELECT content
    FROM document_chunks
    ORDER BY embedding <#> '[{','.join(map(str, query_vec))}]'
    LIMIT {top_k}
    """)

    with engine.connect() as conn:
        result = conn.execute(sql)
        return [{"content": row[0]} for row in result.fetchall()]