from typing import TypeAlias
from typing_extensions import Literal
from langgraph.graph import StateGraph, START, MessagesState, END
from .agent_tools import return_slots
from langgraph.types import Command
import json
import uuid


from .agent_data_definitions import (
    DomainResponse,
    MetaExpertState,
    SlotValueResponse
)
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableSerializable
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
        self.slot_extractor = self.create_slot_extractor()
        self.verifier = self.create_verifier()

    def create_slot_extractor(self) -> RunnableSerializable:
        """
        Created the chain for the slot extractor.

        Args:
            None

        Returns:
            RunnableSerializable:  Chain of prompt with LLM and parser.

        """
        prompt = utils_functions.return_prompt("extract_slots")
        parser = PydanticOutputParser(pydantic_object=SlotValueResponse)

        return prompt | self.model | parser

    def create_verifier(self) -> RunnableSerializable:
        """
        Created the chain for the verifier.

        Args:
            None

        Returns:
            RunnableSerializable:  Chain of prompt with LLM and parser
        """

        prompt = utils_functions.return_prompt("extract_slots")
        parser = PydanticOutputParser(pydantic_object=SlotValueResponse)

        return prompt | self.model | parser

    def domain_extractor_agent(self, state: MetaExpertState) -> Command:
        """
        Domain extractor agent execution handler

        Args:
            state (MetaExpertState): Current state of the system.

        Returns:
            Command: Command to Langgraph to update
        """
        user_prompt = utils_functions.build_last_utterance_prompt(state)
        result = self.domain_extractor.invoke({
            "messages": [{"role": "user", "content": user_prompt}]
        })
        structured: DomainResponse = result["structured_response"]
        domains = structured.domains
        state.push_node("domain_extractor_agent")

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
        user_prompt = utils_functions.build_slot_extraction_prompt(state)
        result = self.slot_extractor.invoke(user_prompt)

        result = {
            key: {"uuid": str(uuid.uuid4())[:8], "value": value}
            for key, value in dict(result)["root"].items()
        }
        print(result)

        state.push_node("slot_extractor_agent")
        updated_conv_list = state.conversation + [{
            "user": state.latest_user_utterance
        }]

        return Command(
            update={
                "extraction_result": result,
                "conversation": updated_conv_list,
                "last_node": state.last_node
            }
        )

    def verifier_agent(self, state: MetaExpertState) -> Command:
        """
        123
        """

    def router_function(self, state: MetaExpertState) -> Command[Literal[
        "domain_extractor_agent", "slot_extractor_agent"
    ]]:
        """
        Takes state of graph and decides next stept.

        Args:
            state (MetaExpertState): Current state of the system.

        Returns:
            Command: Command to execute next node
        """
        # TODO: https://langchain-ai.github.io/langgraph/how-tos/graph-api/#add-retry-policies
        if not bool(state.domains):
            print("Command → domain_extractor_agent")
            return Command(update={}, goto="domain_extractor_agent")
        else:
            print("Command → slot_extractor_agent")
            return Command(update={}, goto="slot_extractor_agent")


class graphState:
    def __init__(
        self,
        conversation: list[dict[str, str]],
        latest_user_utterance: str,
        system: agentSystem
    ):
        self.state: None
        self.conversation = conversation
        self.latest_user_utterance = latest_user_utterance
        self.system = system
        self.graph = self.create_graph()

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
                self.system.router_function,
                "router_function"
            )
            .add_edge(START, "router_function")
            .add_edge("domain_extractor_agent", "router_function")
            .add_edge("slot_extractor_agent", END)
            .compile()
        )
        return graph

    def invoke(self):
        self.state = self.graph.invoke({
            # Kontrolliere bite den Konversation Type
            "conversation": self.conversation,
            "latest_user_utterance": self.latest_user_utterance,
            "domains": [],
            "last_action": [],
            "domain_slots": {},
            "extraction_result": {}
            }
        )

    