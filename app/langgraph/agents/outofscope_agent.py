from app.services.llm_call import LLMService
from app.langgraph.pydantics import OutOfScopeResponse
from app.prompts.outofscope_prompt import OUT_OF_SCOPE_PROMPT
from app.langgraph.state import GraphState
from langchain.output_parsers import PydanticOutputParser

class OutOfScopeAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.parser = PydanticOutputParser(pydantic_object=OutOfScopeResponse)

    def generate_response(self, state: GraphState) -> OutOfScopeResponse:
        """Generate appropriate out-of-scope response using LLM"""
        prompt = OUT_OF_SCOPE_PROMPT.format(
            user_query=state.user_query,
            format_instructions=self.parser.get_format_instructions()
        )
        
        return self.llm_service.generate_response(prompt, self.parser)