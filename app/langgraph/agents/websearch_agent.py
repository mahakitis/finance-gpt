from app.langgraph.tools.search_tool import search_web
from app.langgraph.state import GraphState
from app.langgraph.pydantics import WebSearchResponse

class WebSearchAgent:
    def __init__(self, web_search_tool=None):
        self.web_search_tool = web_search_tool or search_web

    def search(self, state: GraphState) -> WebSearchResponse:
        """Search the web for information"""
        try:
            query = state.rephrased_query or state.user_query
            print(f"Web search query: {query}")
            result = self.web_search_tool(query)
            print(f"Web search result: {result}")
            return result
        except Exception as e:
            print(f"Web search error: {e}")
            return WebSearchResponse(
                success=False,
                error=f"Web search failed: {str(e)}"
            )