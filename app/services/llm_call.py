from groq import Groq
from app.config.config import settings
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from typing import Type
import json
import re

class LLMService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def generate_response(self, prompt: str, parser: PydanticOutputParser, model: str = None) -> BaseModel:
        try:
            model = model or self.model
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful financial assistant. Always respond with valid JSON in the exact format requested."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2048
            )
            response_text = response.choices[0].message.content.strip()
            
            # Clean and parse JSON
            json_content = self._extract_json_from_text(response_text)
            if json_content:
                return parser.pydantic_object(**json_content)
            else:
                return parser.parse(response_text)
                
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._get_default_response(parser.pydantic_object)

    def _extract_json_from_text(self, text: str) -> dict:
        try:
            # Remove any text before first {
            start_idx = text.find('{')
            if start_idx == -1:
                return None
            
            # Find matching closing brace
            brace_count = 0
            end_idx = start_idx
            for i in range(start_idx, len(text)):
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i
                        break
            
            json_str = text[start_idx:end_idx + 1]
            return json.loads(json_str)
        except Exception:
            return None

    def _get_default_response(self, model_class: Type[BaseModel]) -> BaseModel:
        class_name = model_class.__name__
        if class_name == "SupervisorResponse":
            return model_class(decision="intent")
        elif class_name == "IntentResponse":
            return model_class(intent="out_of_scope")
        elif class_name == "RephraseResponse":
            return model_class(rephrased_query="financial query", original_query="financial query")
        elif class_name == "DatabaseLookupResponse":
            return model_class(found=False)
        elif class_name == "SummarizerResponse":
            return model_class(summary="Unable to process request at this time.", sources=[])
        elif class_name == "OutOfScopeResponse":
            return model_class(response="I can only help with financial queries. Please ask about stocks, markets, or company financials.")
        else:
            return model_class()