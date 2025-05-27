from langgraph.graph import StateGraph, START, MessagesState, END
from .agent_tools import return_slots
from langgraph.types import Command
import json


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

    def domain_extractor_agent(self, state: MetaExpertState) -> Command:
        # build your prompt
        user_prompt = dedent(f"""
        <prior_conversation>{state.get('conversation')}</prior_conversation>
        <last_turn>{state.get('latest_user_utterance')}</last_turn>
        """)

        # invoke the agent
        result = self.domain_extractor.invoke({
            "messages": [{"role": "user", "content": user_prompt}]
        })
        structured: DomainResponse = result["structured_response"]
        domains = structured.domains

        return Command(
            update={
                "domains": domains
            }
        )
