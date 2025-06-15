from typing import TypeAlias
from typing_extensions import Literal
from langgraph.graph import StateGraph, START, MessagesState, END
from langgraph.types import Command
import json
import uuid


from .agent_data_definitions import (
    MetaExpertState,
    IssueSolverValue,
    VerificationResponse,
    ExtractionValueResponse
)
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableSerializable
from utils import utils_functions
from textwrap import dedent
from uuid import uuid4


class agentSystem:
    def __init__(
        self,
        yml_slots_path: str,
        model_name="openai:o4-mini-2025-04-16"
    ):
        self.model = init_chat_model(model_name)
        self.slots = utils_functions.read_yml(yml_slots_path)

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
        if prompt_name == "extract_slots":
            parser = PydanticOutputParser(
                pydantic_object=ExtractionValueResponse
            )
        elif prompt_name == "verify_results":
            parser = PydanticOutputParser(pydantic_object=VerificationResponse)
        elif prompt_name == "solve_issue":
            parser = PydanticOutputParser(pydantic_object=IssueSolverValue)

        return prompt | self.model | parser

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

        user_prompt = utils_functions.build_slot_extraction_prompt(
            slots=self.slots,
            latest_user_utterance=state.latest_user_utterance,
            conv=state.conversation
        )
        result = self.slot_extractor.invoke(user_prompt)

        extraction_dict = {}
        root = dict(result.root)
        for key in root.keys():
            temp_dict = dict(root[key])
            temp_dict["context"]
            temp_list = []
            for turn in temp_dict["context"]:
                temp_list.append(dict(turn))
            temp_dict["context"] = temp_list
            temp_dict["slot"] = key
            extraction_dict[str(uuid4())] = temp_dict

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
        user_prompt = utils_functions.build_verification_prompt(
            slots=self.slots,
            latest_user_utterance=state.latest_user_utterance,
            conv=state.conversation,
            extraction_results=state.extraction_result
        )
        result = self.verifier.invoke(user_prompt)

        result = utils_functions.extract_dict_from_pydantic(result)
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
        user_prompt = utils_functions.build_issue_solving_prompt(
            slots=self.slots,
            latest_user_utterance=state.latest_user_utterance,
            conv=state.conversation,
            verifcation_dict=state.last_verification_results
        )
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
            if not verification["boolean"]:
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
        "slot_extractor_agent", "verifier_agent", "issue_solver_agent", END
    ]]:
        """
        Takes state of graph and decides next stept.

        Args:
            state (MetaExpertState): Current state of the system.

        Returns:
            Command: Command to execute next node
        """

        print(state.domains)
        if "no domain found" in state.domains:
            print("Command -> END")
            return Command(
                update={},
                goto=END
            )
        else:
            if not bool(state.extraction_result):
                print("Command -> slot_extractor_agent")
                return Command(update={}, goto="slot_extractor_agent")
            elif "None" in state.extraction_result:
                print("Command -> END")
                return Command(
                    update={},
                    goto=END
                )
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

