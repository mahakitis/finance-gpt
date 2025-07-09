from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class GraphState(BaseModel):
    user_query: str
    session_id: str
    history: List[str] = Field(default_factory=list)
    rephrased_query: Optional[str] = None
    db_result: Optional[str] = None
    web_search_result: Optional[str] = None
    final_answer: Optional[str] = None
    route_decision: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    sources: List[str] = Field(default_factory=list)
    db: Any = None
    
    