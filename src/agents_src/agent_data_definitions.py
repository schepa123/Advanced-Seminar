from typing import TypedDict, Annotated
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages


class MetaExpertState(BaseModel):
    """
    Meta Expert memory slots.
    """

    conversation: list[dict[str, str]] = Field(
        default_factory=list,
        description="A list of the conversation between the meta experts and other agents."
    )
    latest_user_utterance: str = Field(
        default_factory=str,
        description="The latest user utterance."
    )
    domains: list[str] = Field(
        default_factory=list,
        description="Which domains are present in this dialogue turn of the dataset."
    )
    last_action: list[str] = Field(
        default_factory=list,
        description="Last action performed by the multi-agent system."
    )
    extraction_result: dict[str, str] = Field(
        default_factory=dict,
        description="Current results of the extraction process."
    )
    last_verification_results: dict[str, str] = Field(
        default_factory=dict,
        description="Latest results of the verification process."
    )
    last_node: list[str] = Field(
        default_factory=list,
        description="Last node that was executed."
    )

    def push_node(self, node: str):
        self.last_node.append(node)


class DomainResponse(BaseModel):
    """
    Defines response format of domain extractor

    Attributes:
        domains: A list of extracted domains
    """
    domains: list[str]


class SlotDetail(BaseModel):
    """
    Defines for the slots the explanation why it was extracted and
    value extracted
    """
    explanation: str = Field(..., description="Why we extracted this value")
    value: str = Field(..., description="The extracted slot value")


class SlotValueResponse(BaseModel):
    """
    A mapping from *any* slot-name (string) to its SlotDetail.
    """
    __root__: dict[str, SlotDetail]
