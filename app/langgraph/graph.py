from langgraph.graph import StateGraph, END
from app.langgraph.state import GraphState
from app.langgraph.agents.supervisor_agent import SupervisorAgent
from app.langgraph.agents.intent_agent import IntentAgent
from app.langgraph.agents.rephraser_agent import RephraserAgent
from app.langgraph.agents.dblookup_agent import DatabaseLookupAgent
from app.langgraph.agents.websearch_agent import WebSearchAgent
from app.langgraph.agents.summarizer_agent import SummarizerAgent
from app.langgraph.agents.memory_agent import MemoryAgent
from app.langgraph.agents.outofscope_agent import OutOfScopeAgent
from app.services.llm_call import LLMService

class FinanceGPTGraph:
    def __init__(self, vector_db_tool=None, web_search_tool=None, db=None):
        self.llm_service = LLMService()
        self.supervisor = SupervisorAgent(self.llm_service)
        self.intent_agent = IntentAgent(self.llm_service)
        self.rephraser = RephraserAgent(self.llm_service)
        self.db_lookup = DatabaseLookupAgent(vector_db_tool)
        self.web_search = WebSearchAgent(web_search_tool)
        self.summarizer = SummarizerAgent(self.llm_service)
        self.memory = MemoryAgent(db)
        self.out_of_scope = OutOfScopeAgent(self.llm_service)

    def create_graph(self):
        workflow = StateGraph(GraphState)

        workflow.add_node("supervisor", self.supervisor_node)
        workflow.add_node("greeting", self.greeting_node)
        workflow.add_node("intent", self.intent_node)
        workflow.add_node("rephraser", self.rephraser_node)
        workflow.add_node("db_lookup", self.db_lookup_node)
        workflow.add_node("web_search", self.web_search_node)
        workflow.add_node("summarizer", self.summarizer_node)
        workflow.add_node("memory", self.memory_node)
        workflow.add_node("out_of_scope", self.out_of_scope_node)

        workflow.set_entry_point("supervisor")

        workflow.add_conditional_edges("supervisor", self.supervisor_router, {
            "greeting": "greeting",
            "intent": "intent",
            "rephrase": "rephraser"
        })

        workflow.add_conditional_edges("intent", self.intent_router, {
            "financial_query": "rephraser",
            "greeting": "greeting",
            "out_of_scope": "out_of_scope"
        })

        workflow.add_edge("greeting", END)
        workflow.add_edge("out_of_scope", END)
        workflow.add_edge("rephraser", "db_lookup")

        workflow.add_conditional_edges("db_lookup", self.db_lookup_router, {
            "found": "summarizer",
            "not_found": "web_search"
        })

        workflow.add_edge("web_search", "summarizer")
        workflow.add_edge("summarizer", "memory")
        workflow.add_edge("memory", END)

        return workflow.compile()

    def supervisor_node(self, state: GraphState) -> GraphState:
        try:
            result = self.supervisor.analyze(state)
            state.route_decision = result.decision
        except Exception as e:
            print(f"Supervisor error: {e}")
            state.route_decision = "intent"
        return state

    def greeting_node(self, state: GraphState) -> GraphState:
        greeting_prompt = f"""
        You are FinanceGPT, a warm, professional financial assistant. 
        Respond directly to the user's greeting with a friendly introduction in a single line.
        User said: "{state.user_query}"
        Reply:
        """
        
        try:
            response = self.llm_service.client.chat.completions.create(
                model=self.llm_service.model,
                messages=[{"role": "user", "content": greeting_prompt}],
                temperature=0.7,
                max_tokens=150
            )
            state.final_answer = response.choices[0].message.content.strip()
        except Exception:
            state.final_answer = "Hello! I'm FinanceGPT, your financial assistant. How can I help you with financial information today?"
        
        return state

    def intent_node(self, state: GraphState) -> GraphState:
        try:
            result = self.intent_agent.classify(state)
            state.route_decision = result.intent
        except Exception as e:
            print(f"Intent error: {e}")
            state.route_decision = "out_of_scope"
        return state

    def rephraser_node(self, state: GraphState) -> GraphState:
        try:
            result = self.rephraser.rephrase(state)
            state.rephrased_query = result.rephrased_query
        except Exception as e:
            print(f"Rephraser error: {e}")
            state.rephrased_query = state.user_query
        return state

    def db_lookup_node(self, state: GraphState) -> GraphState:
        try:
            result = self.db_lookup.search(state)
            if result.found and result.answer:
                state.db_result = result.answer
                state.route_decision = "found"
                if result.source:
                    state.sources.append(result.source)
            else:
                state.route_decision = "not_found"
        except Exception as e:
            print(f"DB lookup error: {e}")
            state.route_decision = "not_found"
        return state

    def web_search_node(self, state: GraphState) -> GraphState:
        try:
            result = self.web_search.search(state)
            
            if result and result.success:
                state.web_search_result = result.content
                if result.sources:
                    state.sources.extend(result.sources)
            else:
                error_msg = result.error if result else "Unknown error"
                state.web_search_result = f"Web search failed: {error_msg}"
                
        except Exception as e:
            print(f"Web search error: {e}")
            state.web_search_result = f"Web search error: {str(e)}"
        return state

    def summarizer_node(self, state: GraphState) -> GraphState:
        try:
            result = self.summarizer.summarize(state)
            state.final_answer = result.summary
            if result.sources:
                state.sources.extend(result.sources)
        except Exception as e:
            print(f"Summarizer error: {e}")
            # Fallback to basic response
            content = state.db_result or state.web_search_result
            if content and not content.startswith("Web search failed"):
                state.final_answer = f"Based on available information: {content[:500]}..."
            else:
                state.final_answer = "I apologize, but I couldn't find relevant information for your query."
        return state

    def memory_node(self, state: GraphState) -> GraphState:
        try:
            return self.memory.save_interaction(state)
        except Exception as e:
            print(f"Memory error: {e}")
            return state

    def out_of_scope_node(self, state: GraphState) -> GraphState:
        try:
            result = self.out_of_scope.generate_response(state)
            state.final_answer = result.response
        except Exception as e:
            print(f"Out of scope error: {e}")
            state.final_answer = "I'm a financial assistant and can help with finance-related questions. Please ask about stocks, markets, or company financials."
        return state

    def supervisor_router(self, state: GraphState) -> str:
        return state.route_decision or "intent"

    def intent_router(self, state: GraphState) -> str:
        return state.route_decision or "out_of_scope"

    def db_lookup_router(self, state: GraphState) -> str:
        return state.route_decision or "not_found"