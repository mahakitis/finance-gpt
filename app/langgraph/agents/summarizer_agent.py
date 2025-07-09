from app.services.llm_call import LLMService
from app.langgraph.state import GraphState
from app.langgraph.pydantics import SummarizerResponse
from app.prompts.summarizer_prompt import SUMMARIZER_PROMPT
from langchain.output_parsers import PydanticOutputParser

class SummarizerAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.parser = PydanticOutputParser(pydantic_object=SummarizerResponse)

    def summarize(self, state: GraphState) -> SummarizerResponse:
        """Summarize findings and create final answer"""
        try:
            content = state.db_result or state.web_search_result or "No information found"
            
            prompt = SUMMARIZER_PROMPT.format(
                user_query=state.user_query,
                content=content,
                sources=", ".join(state.sources) if state.sources else "No sources",
                format_instructions=self.parser.get_format_instructions()
            )
            
            return self.llm_service.generate_response(prompt, self.parser)
            
        except Exception as e:
            print(f"Summarizer error: {e}")
            return SummarizerResponse(
                summary="I apologize, but I encountered an error while processing your request. Please try again.",
                sources=state.sources or []
            )