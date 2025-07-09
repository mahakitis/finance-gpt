from app.services.llm_call import LLMService
from app.langgraph.state import GraphState
from app.langgraph.pydantics import SupervisorResponse
from app.prompts.supervisor_prompt import SUPERVISOR_PROMPT
from langchain.output_parsers import PydanticOutputParser

class SupervisorAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.parser = PydanticOutputParser(pydantic_object=SupervisorResponse)

    def analyze(self, state: GraphState) -> SupervisorResponse:
        """Analyze user query and decide routing"""
        prompt = SUPERVISOR_PROMPT.format(
            user_query=state.user_query,
            history="\n".join(state.history) if state.history else "No previous conversation",
            format_instructions=self.parser.get_format_instructions()
        )
        
        return self.llm_service.generate_response(prompt, self.parser)