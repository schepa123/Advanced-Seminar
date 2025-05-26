from langgraph.graph import StateGraph, START, MessagesState, END
from .agent_tools import return_slots
from langgraph.types import Command

from .agent_data_definitions import DomainResponse, MetaExpertState
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from utils import utils_functions
from textwrap import dedent



class agentSystem:
    def __init__(self, model_name="openai:o4-mini-2025-04-16"):
        self.model = init_chat_model(model_name)
        self.domain_extractor = create_react_agent(
            model=self.model,
            tools=[return_slots],
            prompt=utils_functions.return_prompt("detect_domain"),
            response_format=DomainResponse
        )

    def domain_extractor_agent(self, state: MetaExpertState):
        user_prompt = dedent(f"""
        <prior_conversation>{state.get('conversation')}</prior_conversation>
        <last_turn>{state.get('last_action')}</last_turn>
        """)

        response = self.domain_extractor.invoke(
            {"messages": [{"role": "user", "content": user_prompt}]}
        )
        # Extract relevant updates from response (adjust as needed)
        updated_domains = response.get("domains", [])

        # Return updated state and control flow (e.g., continue or route)
        return Command(
            update={
                "domains": updated_domains
            }
        )
