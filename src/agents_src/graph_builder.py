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
    SlotValueResponse,
    VerificationResponse
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
        self.slot_extractor = self.create_agent(prompt_name="extract_slots")
        self.verifier = self.create_agent(prompt_name="verify_results")
        self.issue_solver = self.create_agent(prompt_name="solve_issue")

    def create_agent(self, prompt_name) -> RunnableSerializable:
        """
        Creates the chain for an agent.

        Args:
            None
        Returns:
            RunnableSerializable:  Chain of prompt with LLM and parser.
        """
        prompt = utils_functions.return_prompt(prompt_name)
        if prompt_name == "extract_slots" or prompt_name == "solve_issue":
            parser = PydanticOutputParser(pydantic_object=SlotValueResponse)
        elif prompt_name == "verify_results":
            parser = PydanticOutputParser(pydantic_object=VerificationResponse)

        return prompt | self.model | parser

    def domain_extractor_agent(self, state: MetaExpertState) -> Command:
        """
        Domain extractor agent execution handler

        Args:
            state (MetaExpertState): Current state of the system.

        Returns:
            Command: Command to Langgraph to update
        """
        print("domain_extractor_agent")
        user_prompt = utils_functions.build_last_utterance_prompt(state)
        result = self.domain_extractor.invoke({
            "messages": [{"role": "user", "content": user_prompt}]
        })
        structured: DomainResponse = result["structured_response"]
        domains = structured.domains
        state.push_node("domain_extractor_agent")
        print(f"state.last_node: {state.last_node}")

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
        print("slot_extractor_agent")
        user_prompt = utils_functions.build_slot_extraction_prompt(state)
        result = self.slot_extractor.invoke(user_prompt)

        result = {
            key: {"uuid": str(uuid.uuid4())[:8], "value": dict(value)}
            for key, value in dict(result)["root"].items()
        }
        print(result)

        state.push_node("slot_extractor_agent")

        return Command(
            update={
                "extraction_result": result,
                "last_node": state.last_node
            }
        )

    def verifier_agent(self, state: MetaExpertState) -> Command:
        """
        Verifies the extracted slot-value pairs.

        Args:
            state (MetaExpertState): Current state of the system.

        Returns:
            Command: Command to update `last_verification_results` and `last_node`
            fields of state.
        """
        print("verifier_agent")
        user_prompt = utils_functions.build_verification_prompt(state)
        result = self.verifier.invoke(user_prompt)

        result = {
            key: value
            for key, value in dict(result)["root"].items()
        }
        state.push_node("verifier_agent")
        return Command(
            update={
                "last_verification_results": result,
                "last_node": state.last_node
            }
        )

    def issue_solver_agent(self, state: MetaExpertState) -> Command:
        """
        Solves issues found in verifcation process

        Args:
            state (MetaExpertState): Current state of the system.

        Returns:
            Command: Command to update `extraction_result` and `last_node`
            fields of state.
        """
        print("issue_solver_agent")
        user_prompt = utils_functions.build_verification_prompt(state)
        result = self.verifier.invoke(user_prompt)
        result = {
            key: value
            for key, value in dict(result)["root"].items()
        }
        state.push_node("issue_solver_agent")
        return Command(
            update={
                "issue_solver": result,
                "last_node": state.last_node
            }
        )

    def check_if_wrong_result(self, state: MetaExpertState) -> bool:
        """
        Checks if any element was verified as false
        in the verification process.

        Args:
            state (MetaExpertState): Current state of the system.

        Returns:
            bool: Trure if any result was verified as false;
            false otherwise
        """
        for _, verification in state.last_verification_results.items():
            if not dict(verification)["boolean"]:
                return True
        return False

    def check_if_verification_finished(
        self, state: MetaExpertState
    ) -> Command[Literal["verifier_agent", "issue_solver_agent", END]]:
        """
        123
        """
        last_agent = state.last_node[-1]

        if last_agent in ("slot_extractor_agent", "issue_solver_agent"):
            print("Command -> verifier_agent")
            return Command(update={}, goto="verifier_agent")

        if last_agent == "verifier_agent":
            if self.check_if_wrong_result(state):
                print("Command -> issue_solver_agent")
                return Command(update={}, goto="issue_solver_agent")

            # verification succeeded
            print("Command -> END")
            updated_conv = state.conversation + [
                {"user": state.latest_user_utterance}
            ]
            return Command(
                update={"conversation": updated_conv},
                goto=END
            )

    def router_function(self, state: MetaExpertState) -> Command[Literal[
        "domain_extractor_agent", "slot_extractor_agent", "verifier_agent",
        "issue_solver_agent", END
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
            print("Command -> domain_extractor_agent")
            return Command(update={}, goto="domain_extractor_agent")
        else:
            if not bool(state.extraction_result):
                print("Command -> slot_extractor_agent")
                return Command(update={}, goto="slot_extractor_agent")
            else:
                return self.check_if_verification_finished(state)


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
                self.system.verifier_agent,
                "verifier_agent"
            )
            .add_node(
                self.system.issue_solver_agent,
                "issue_solver_agent"
            )
            .add_node(
                self.system.router_function,
                "router_function"
            )
            .add_edge(START, "router_function")
            .add_edge("domain_extractor_agent", "router_function")
            
            .add_edge("slot_extractor_agent", "router_function")
            .add_edge("verifier_agent", "router_function")
            .add_edge("issue_solver_agent", "router_function")
            .add_edge("router_function", END)
            .compile()
        )
        return graph

    def invoke(self, state=None):
        if state is None:
            self.state = self.graph.invoke({
                "conversation": self.conversation,
                "latest_user_utterance": self.latest_user_utterance,
                "domains": [],
                "last_action": [],
                "domain_slots": {},
                "extraction_result": {}
                }
            )
        else:
            self.state = self.graph.invoke({
                "conversation": state.conversation,
                "latest_user_utterance": state.latest_user_utterance,
                "domains": state.domains,
                "last_action": state.last_action,
                "domain_slots": {},
                "extraction_result": state.extraction_result
                }
            )

