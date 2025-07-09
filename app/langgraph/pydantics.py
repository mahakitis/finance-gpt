from pydantic import BaseModel, Field
from typing import Literal, Optional, List

class SupervisorResponse(BaseModel):
    decision: Literal["greeting", "intent", "rephrase"]
    message: Optional[str] = None

class IntentResponse(BaseModel):
    intent: Literal["financial_query", "greeting", "out_of_scope"]
    confidence: Optional[float] = None
    message: Optional[str] = None

class RephraseResponse(BaseModel):
    rephrased_query: str
    original_query: str
    changes_made: Optional[str] = None

class DatabaseLookupResponse(BaseModel):
    found: bool
    answer: Optional[str] = None
    source: Optional[str] = None

class WebSearchResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    sources: List[str] = Field(default_factory=list)
    error: Optional[str] = None

class SummarizerResponse(BaseModel):
    summary: str
    sources: List[str] = Field(default_factory=list)

class OutOfScopeResponse(BaseModel):
    response: str
    suggestion: Optional[str] = None