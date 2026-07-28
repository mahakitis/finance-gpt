from sqlalchemy import text
from app.db_utils.database import engine
from app.services.embeddings import embed_chunks

def search_pgvector(query: str, top_k=5) -> list[dict]:
    query_vec = embed_chunks([query])[0]
    sql = text(f"""
    SELECT content
    FROM document_chunks
    ORDER BY embedding <#> '[{','.join(map(str, query_vec))}]'
    LIMIT {top_k}
    """)

    with engine.connect() as conn:
        result = conn.execute(sql)
        return [{"content": row[0]} for row in result.fetchall()]