import requests
from app.config.config import settings
from app.langgraph.pydantics import WebSearchResponse

def search_web(query: str) -> WebSearchResponse:
    """Search the web directly via Tavily API with error handling"""
    try:
        if not settings.TAVILY_API_KEY:
            return WebSearchResponse(
                success=False, 
                error="Tavily API key not configured in settings"
            )
        
        url = "https://api.tavily.com/search"
        headers = {"Content-Type": "application/json"}
        payload = {
            "api_key": settings.TAVILY_API_KEY,
            "query": query,
            "search_depth": "basic",  # or "advanced" if needed
            "include_answer": False,
            "include_raw_content": True,
            "max_results": 5
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        if not results:
            return WebSearchResponse(success=False, error="No results found from Tavily")

        content = "\n\n".join(
            r.get("content", "")[:500] + "..." if len(r.get("content", "")) > 500 else r.get("content", "")
            for r in results if r.get("content")
        )

        sources = [r.get("url") for r in results if r.get("url")]

        return WebSearchResponse(
            success=True,
            content=content,
            sources=sources
        )

    except requests.exceptions.RequestException as e:
        return WebSearchResponse(success=False, error=f"Request error: {str(e)}")
    except Exception as e:
        return WebSearchResponse(success=False, error=f"Unexpected error: {str(e)}")
