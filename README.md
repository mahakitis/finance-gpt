# 📊 FinanceGPT

A finance-focused RAG chatbot that answers questions grounded in your own uploaded financial documents (PDF/DOCX/TXT), falls back to live web search for real-time data like stock prices, and politely declines anything outside its finance scope — with conversational memory across turns.

**Live demo:** _add your Streamlit Cloud link here once deployed_
**API:** _add your Render URL here once deployed_

---

## ✨ Features

- **Document Q&A** — upload financial PDFs/DOCX/TXT; they're chunked, embedded, and stored in Postgres with `pgvector` for semantic retrieval.
- **Live market data** — for questions that need current info (e.g. "what's TCS's stock price today"), a web-search agent (Tavily) supplements the answer.
- **Scoped, honest answers** — an intent-classification step routes clearly out-of-scope questions (non-finance topics) to an "I'm not able to help with that" response instead of hallucinating.
- **Conversational memory** — each chat session persists its Q&A history in the database, so follow-up questions ("what about last quarter?") are answered with prior context.
- **Multi-agent pipeline** — built with LangGraph: a supervisor agent routes each query through intent classification, document lookup, web search, summarization, or the out-of-scope handler as needed.

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────────────────┐
│  Streamlit   │─────▶│   FastAPI Backend │─────▶│   LangGraph Multi-Agent  │
│  Frontend    │◀─────│  (upload/query/   │◀─────│   Pipeline (Groq LLM)    │
└─────────────┘      │   session routes) │      └─────────────────────────┘
                       └────────┬─────────┘                   │
                                │                    ┌─────────┴─────────┐
                                ▼                    ▼                   ▼
                       ┌─────────────────┐   ┌──────────────┐   ┌───────────────┐
                       │ Postgres +       │   │ Tavily Web   │   │ sentence-      │
                       │ pgvector         │   │ Search       │   │ transformers   │
                       │ (Supabase)       │   │              │   │ (embeddings)   │
                       └─────────────────┘   └──────────────┘   └───────────────┘
```

**Agent flow per query:** Supervisor → Intent Classifier → (Doc Lookup and/or Web Search, as needed) → Rephraser/Summarizer → Memory Agent (persists the turn) → Final Answer.

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| Orchestration | LangGraph |
| LLM | Groq (Llama 3.3) |
| Web search | Tavily |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`, 384-dim) |
| Vector store | PostgreSQL + pgvector (hosted on Supabase) |
| Migrations | Alembic |
| Frontend | Streamlit |
| Dependency management | Poetry |

## 📁 Project Structure

```
finance-gpt/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── routers/              # upload, query, session endpoints
│   ├── services/              # chunking, embeddings, retrieval, LLM calls
│   ├── langgraph/              # multi-agent graph + individual agents
│   ├── models/                # SQLAlchemy models
│   ├── schemas/                # Pydantic request/response schemas
│   └── db_utils/                # DB session management
├── alembic/                      # database migrations
├── src/
│   ├── app.py                     # Streamlit frontend
│   └── requirements.txt            # lightweight deps for frontend-only deploys
└── pyproject.toml
```

## 🚀 Local Setup

### Prerequisites
- Python 3.12+
- [Poetry](https://python-poetry.org/)
- A Postgres database with the `pgvector` extension enabled (e.g. a free [Supabase](https://supabase.com) project)
- API keys: [Groq](https://console.groq.com) (free), [Tavily](https://tavily.com) (free tier)

### Install dependencies
```bash
poetry install --no-root
```

### Configure environment
Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/postgres
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
GROQ_MODEL=llama-3.3-70b-versatile
```

### Run migrations
```bash
poetry run alembic upgrade head
```

### Start the backend
```bash
poetry run uvicorn app.main:app --reload
```
API docs available at `http://127.0.0.1:8000/docs`.

### Start the frontend
```bash
cd src
poetry run streamlit run app.py
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/session/create` | Start a new chat session |
| `GET` | `/session/{session_id}/history` | Retrieve past turns for a session |
| `POST` | `/upload/document` | Upload & embed a document |
| `POST` | `/query` | Ask a question (grounded + context-aware) |

## ☁️ Deployment

- **Backend**: deployed on [Render](https://render.com) as a web service (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`).
- **Frontend**: deployed on [Streamlit Community Cloud](https://share.streamlit.io), pointed at `src/app.py`, with `FINANCEGPT_API_URL` set as a secret to the deployed backend URL.
- **Database**: hosted on [Supabase](https://supabase.com) (Postgres + pgvector).

## 🔭 Possible Future Improvements

- Multi-turn source citation display in the UI
- Support for streaming responses
- Multi-document comparison queries
- User-level authentication (currently session-based, not account-based)

## 📄 License

_Add a license if you'd like this to be reusable by others (MIT is a common default for portfolio projects)._