from app.langgraph.state import GraphState
from app.langgraph.pydantics import DatabaseLookupResponse
from app.services.retriever import search_pgvector

class DatabaseLookupAgent:
    def __init__(self, vector_db_tool=None):
        self.vector_db_tool = vector_db_tool or search_pgvector

    def _is_relevant_result(self, query: str, result: str) -> bool:
        if not result or len(result.strip()) < 20:
            return False

        query_lower = query.lower()
        result_lower = result.lower()

        # Check for financial relevance
        financial_keywords = ['revenue', 'profit', 'earnings', 'sales', 'income', 'financial', 'report', 'annual', 'stock', 'market', 'investment']
        query_has_financial = any(keyword in query_lower for keyword in financial_keywords)

        if query_has_financial:
            financial_indicators = [
                '$', 'million', 'billion', 'revenue', 'profit', 'earnings',
                'sales', 'income', 'crore', '%', 'percent', 'assets', 'liabilities',
                'growth', 'performance', 'quarter', 'year'
            ]
            return any(indicator in result_lower for indicator in financial_indicators)

        return True

    def search(self, state: GraphState) -> DatabaseLookupResponse:
        try:
            query = state.rephrased_query or state.user_query
            results = self.vector_db_tool(query)

            if results:
                for result in results:
                    content = result.get("content", "")
                    if self._is_relevant_result(query, content):
                        return DatabaseLookupResponse(
                            found=True,
                            answer=content,
                            source="internal_db"
                        )
            return DatabaseLookupResponse(found=False)
        except Exception as e:
            print(f"Database lookup error: {e}")
            return DatabaseLookupResponse(found=False)