from app.schemas.query_schema import QueryRequest, QueryResponse
from app.langgraph.graph import FinanceGPTGraph
from app.langgraph.agents.memory_agent import MemoryAgent
from app.langgraph.state import GraphState

def process_query(payload: QueryRequest, db):
    """Process query with proper error handling"""
    try:
        agent = MemoryAgent(db)
        history = agent.get_history(payload.session_id)

        state = GraphState(
            user_query=payload.query,
            session_id=payload.session_id,
            history=history,
            db=db
        )

        graph = FinanceGPTGraph(db=db)
        compiled_graph = graph.create_graph()
        result = compiled_graph.invoke(state.model_dump())

        return QueryResponse(answer=result.get("final_answer", "Unable to process query"))

    except Exception:
        return QueryResponse(answer="I encountered an error. Please try again.")
