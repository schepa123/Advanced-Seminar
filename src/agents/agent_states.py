from typing import TypedDict


class MetaExpertState(TypedDict, total=False):
    """
    Meta Expert memory slots.

    Attributes:
        conversation: A list of the conversation between
        the meta experts and other agents.
        domains: Which domains are present in this dialogue
        turn of the dataset.
        last_action: Last action performed by the multi agent
        system.
        domain_slots: Dict of slots for each domain
    """
    conversation: list[str]
    domains: list[str]
    last_action: list[str]
    domain_slots: dict[str, dict[str, str]]
