from app.services.llm_call import LLMService
from app.langgraph.state import GraphState
from app.langgraph.pydantics import RephraseResponse
from app.prompts.rephraser_prompt import REPHRASER_PROMPT
from langchain.output_parsers import PydanticOutputParser

class RephraserAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.parser = PydanticOutputParser(pydantic_object=RephraseResponse)

    def rephrase(self, state: GraphState) -> RephraseResponse:
        """Rephrase user query for better search"""
        prompt = REPHRASER_PROMPT.format(
            user_query=state.user_query,
            context=state.context or {},
            history="\n".join(state.history) if state.history else "No previous conversation",
            format_instructions=self.parser.get_format_instructions()
        )
        
        return self.llm_service.generate_response(prompt, self.parser)