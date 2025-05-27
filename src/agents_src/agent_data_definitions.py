from typing import TypedDict, Annotated
from pydantic import BaseModel
from langgraph.graph.message import add_messages



class MetaExpertState(TypedDict, total=False):
    """
    Meta Expert memory slots.

    Attributes:
        conversation: A list of the conversation between
        the meta experts and other agents.
        latest_user_utterance: The latest user utterance
        domains: Which domains are present in this dialogue
        turn of the dataset.
        last_action: Last action performed by the multi agent
        system.
        domain_slots: Dict of slots for each domain.
        extraction_results: Current results of the extraction process.
        last_verification_results: Latest results of the verification
        process.
    """
    conversation: list[str]
    latest_user_utterance: str
    domains: list[str]
    last_action: list[str]
    domain_slots: dict[str, dict[str, str]]
    extraction_result: dict[str, str]
    last_verification_results: dict[str, str]
    last_node: Annotated[list[str], add_messages]


class DomainResponse(BaseModel):
    """
    Defines response format of domain extractor

    Attributes:
        domains: A list of extracted domains
    """
    domains: list[str]
