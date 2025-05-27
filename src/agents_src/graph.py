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
        """
        Extracts the domain from the last turn of a conversation.

        Args:
            state (MetaExpertState): Current state of the system.

        Returns:
            Command: Command to update `domain` and `last_node`
            fields of state.
        """
        user_prompt = utils_functions.build_last_utterance_prompt(state)

        # invoke the agent
        result = self.domain_extractor.invoke({
            "messages": [{"role": "user", "content": user_prompt}]
        })
        structured: DomainResponse = result["structured_response"]
        domains = structured.domains

        return Command(
            update={
                "domains": domains,
                "last_node": ["domain_extractor_agent"]
            }
        )

    def extractor_agent(self, state: MetaExpertState) -> Command:
        """
        123
        """
        user_prompt = utils_functions.build_last_utterance_prompt(state)


class graphState:
    def __init__(
        self,
        conversation: list[str],
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
        self.graph = None
        self.system = system 

    def create_graph(self):
        graph = (
            StateGraph(MetaExpertState)
            .add_node(
                self.system.domain_extractor_agent,
                "domain_extractor_agent"
            )
            .add_node(print_yes, "print_yes")
            .add_node(step_done, "step_done")
            .add_edge(START, "step_done")
            .add_conditional_edges(
                "step_done",
                lambda st: not bool(st.get("domains")),
                {True: "domain_extractor_agent", False: "print_yes"},
            )
            .add_edge("domain_extractor_agent", "step_done")
            .add_edge("print_yes", END)
            .compile()
        )