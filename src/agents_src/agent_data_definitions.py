from typing import TypedDict, Annotated
from pydantic import BaseModel, Field, RootModel
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
        print(f"self.last_node: {self.last_node}")


class SpeakerUtterance(BaseModel):
    speaker: str = Field(..., description="The role of the speaker")
    utterance: str = Field(..., description="Utterance by speaker")


class SlotDetail(BaseModel):
    """
    Defines for the slots the explanation why it was extracted and
    value extracted
    """
    explanation: str = Field(..., description="Why we extracted this value")
    value: str = Field(..., description="The extracted slot value")
    context: list[SpeakerUtterance] = Field(
        ...,
        description="The contexted surrounding the value"
    )


class SlotValueResponse(RootModel[dict[str, SlotDetail]]):

    """
    A mapping from *any* slot-name (string) to its SlotDetail.
    """
    pass
