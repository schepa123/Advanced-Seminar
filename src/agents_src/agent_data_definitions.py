from typing import TypedDict
from pydantic import BaseModel


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
    """
    conversation: list[str]
    latest_user_utterance: str
    domains: list[str]
    last_action: list[str]
    domain_slots: dict[str, dict[str, str]]


class DomainResponse(BaseModel):
    """
    Defines response format of domain extractor

    Attributes:
        domains: A list of extracted domains
    """
    domains: list[str]
