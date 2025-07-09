from app.langgraph.state import GraphState
from datetime import datetime
from sqlalchemy import text

class MemoryAgent:
    def __init__(self, db):
        self.db = db

    def get_history(self, session_id: str) -> list[str]:
        """Retrieve chat history from the DB for a given session"""
        try:
            sql = text("""
                SELECT question, answer
                FROM memory_nodes
                WHERE session_id = :session_id
                ORDER BY created_at
            """)
            result = self.db.execute(sql, {"session_id": session_id})
            history = [f"Q: {row.question}\nA: {row.answer}" for row in result]
            return history
        except Exception:
            self.db.rollback()
            return []

    def save_interaction(self, state: GraphState):
        """Save user interaction for future context"""
        try:
            interaction = {
                "session_id": state.session_id,
                "user_query": state.user_query,
                "final_answer": state.final_answer,
                "timestamp": datetime.now(),
                "sources": ", ".join(state.sources)
            }

            sql = text("""
                INSERT INTO memory_nodes (session_id, question, answer, created_at, sources)
                VALUES (:session_id, :user_query, :final_answer, :timestamp, :sources)
            """)

            self.db.execute(sql, interaction)
            self.db.commit()

            state.history.append(f"Q: {state.user_query}")
            state.history.append(f"A: {state.final_answer}")

            return state
        except Exception:
            self.db.rollback()
            return state
