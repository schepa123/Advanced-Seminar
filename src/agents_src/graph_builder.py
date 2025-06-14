from typing import TypeAlias
from typing_extensions import Literal
from langgraph.graph import StateGraph, START, MessagesState, END
from langgraph.types import Command
import json
import uuid


from .agent_data_definitions import (
    MetaExpertState,
    SlotValueResponse#,
#    VerificationResponse
)
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableSerializable
from utils import utils_functions
from textwrap import dedent


class agentSystem:
    def __init__(
        self,
        yml_slots_path: str,
        model_name="openai:o4-mini-2025-04-16"
    ):
        self.model = init_chat_model(model_name)
        self.slots = utils_functions.read_yml(yml_slots_path)

        #self.domain_extractor = self.create_agent(prompt_name="detect_domain")
        self.slot_extractor = self.create_agent(prompt_name="extract_slots")
        self.verifier = self.create_agent(prompt_name="verify_results")
        #self.issue_solver = self.create_agent(prompt_name="solve_issue")

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
        


