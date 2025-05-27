from typing import TypeAlias
from typing_extensions import Literal
from langgraph.graph import StateGraph, START, MessagesState, END
from .agent_tools import return_slots
from langgraph.types import Command
import json


from .agent_data_definitions import DomainResponse, MetaExpertState
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain.chains import LLMChain
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
        self.slot_extractor_agent = LLMChain(
            llm=self.model,
            prompt=utils_functions.return_prompt("extract_slots")
        )

    def domain_extractor_agent(self, state: MetaExpertState) -> Command:

        user_prompt = utils_functions.build_last_utterance_prompt(state)

        # invoke the agent
        result = self.domain_extractor.invoke({
            "messages": [{"role": "user", "content": user_prompt}]
        })
        structured: DomainResponse = result["structured_response"]
        domains = structured.domains

        state.push_node("domain_extractor_agent")
        print(domains)

        return Command(
            update={
                "domains": (
                    utils_functions.fix_common_spelling_mistakes(domains)
                ),
                "last_node": state.last_node
            }
        )

    def slot_extractor_agent(self, state: MetaExpertState) -> Command:
        """
        Extracts the slot-value pairs from the latest user utterance.

        Args:
            state (MetaExpertState): Current state of the system.

        Returns:
            Command: Command to update `extraction_result` and `last_node`
            fields of state.
        """
        user_prompt = utils_functions.build_last_utterance_prompt(state)


class graphState:
    def __init__(
        self,
        conversation: list[dict[str, str]],
        lattest_user_utterance: str,
        system: agentSystem
    ):
        self.state: MetaExpertState = {
            # Kontrolliere bite den Konversation Type
            "conversation": conversation,
            "latest_user_utterance": lattest_user_utterance,
            "domains": [],
            "last_action": [],
            "domain_slots": {}
        }
        self.graph = self.create_graph()
        self.system = system

    def create_graph(self):
        graph = (
            StateGraph(MetaExpertState)
            .add_node(
                self.system.domain_extractor_agent,
                "domain_extractor_agent"
            )
            .add_node(
                self.system.slot_extractor_agent,
                "slot_extractor_agent"
            )
            .add_node(
                self.router_function,
                "router"
            )
            .add_edge(START, "router")
            .add_edge("domain_extractor_agent", "router")
            .add_edge("slot_extractor_agent", "router")
            .add_conditional_edges(
                "router",
                self.router,
                {
                    
                }
                
            )

            .add_node(print_yes, "print_yes")
            .add_node(step_done, "step_done")
            .add_edge(START, "step_done")
            .add_conditional_edges(
                "step_done",
                lambda st: not bool(st.domains),
                {True: "domain_extractor_agent", False: "print_yes"},
            )
            .add_edge("domain_extractor_agent", "step_done")
            .add_edge("print_yes", END)
            .compile()
        )

    def router(self) -> Literal[
        "domain_extractor_agent", "slot_extractor_agent", "__end__"
    ]:
        if not bool(self.state.domains):
            return "domain_extractor_agent"
        else:
            return "slot_extractor_agent"
