from app.services.llm_call import LLMService
from app.langgraph.state import GraphState
from app.langgraph.pydantics import IntentResponse
from app.prompts.intent_prompt import INTENT_CLASSIFICATION_PROMPT
from langchain.output_parsers import PydanticOutputParser

class IntentAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.parser = PydanticOutputParser(pydantic_object=IntentResponse)

    def classify(self, state: GraphState) -> IntentResponse:
        """Classify user intent using LLM"""
        prompt = INTENT_CLASSIFICATION_PROMPT.format(
            user_query=state.user_query,
            history="\n".join(state.history) if state.history else "No previous conversation",
            format_instructions=self.parser.get_format_instructions()
        )
        
        return self.llm_service.generate_response(prompt, self.parser)