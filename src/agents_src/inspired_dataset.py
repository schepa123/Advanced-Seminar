import pandas as pd
import os
import json
from uuid import uuid4
from .graph_builder import agentSystem, graphState
from utils import utils_functions


class inspiredDataset:
    def __init__(self, path: str, yml_slots_path) -> None:
        self.path = path
        self.conversations = self.create_conversation_data()
        self.agents = agentSystem(yml_slots_path=yml_slots_path)

    def create_conversation_data(self) -> dict[str, list[dict[str, str]]]:
        """
        Loads the conversation data and creates conversation dicts
        out of it.

        Args:
            None.

        Returns:
            dict[str, dict[str, str]]: Conversation with keys 'speaker',
            'utterance', 'recommend'
        """
        collection_conversations = {}
        with open(self.path, 'r') as j:
            dialogues = json.loads(j.read())
        for dialog in dialogues:
            conversation = []
            dialog = dialog["dialog"]
            speaker = dialog[0]["role"].lower()
            utterance = dialog[0]["utterance"]
            for turn in dialog[1:]:
                row_speaker = turn["role"].lower()
                row_text = turn["utterance"]
                row_movies = turn["movies"]
                is_recommendation = (
                    row_speaker == "recommender"
                    and row_movies
                )
                if is_recommendation:
                    conversation.append({
                        "speaker": speaker,
                        "utterance": utterance.replace(
                            "QUOTATION_MARK",
                            ""
                        ),
                        "recommend": False,
                    })
                    conversation.append({
                        "speaker": row_speaker,
                        "utterance": row_text.replace(
                            "QUOTATION_MARK",
                            ""
                        ),
                        "recommend": True,
                        "movies": row_movies
                    })
                    speaker = ""
                    utterance = ""
                else:
                    if speaker != row_speaker and utterance != "":
                        conversation.append({
                            "speaker": speaker,
                            "utterance": utterance.replace(
                                "QUOTATION_MARK",
                                ""
                            ),
                            "recommend": False
                        })
                        utterance = row_text
                        speaker = row_speaker
                    else:
                        utterance = f"{utterance}\n{row_text}"
                        speaker = row_speaker
            collection_conversations[str(uuid4())] = conversation

        return collection_conversations

    def old_dataset_create(self) -> dict[str, dict[str, str]]:
        """
        Loads the conversation data and creates conversation dicts
        out of it.

        Args:
            None.

        Returns:
            dict[str, dict[str, str]]: Conversation with keys 'speaker',
            'utterance', 'recommend'
        """
        # df = pd.read_csv("/home/benedikt-baumgartner/train.tsv", sep="\t")
        # dialogue_ids = list(df["dialog_id"].unique())
        collection_conversations = {}
        with open(self.path, 'r') as j:
            dialogues = json.loads(j.read())
        for dialogue in dialogues:
            temp = df[df["dialog_id"] == dialogue_id][
                ["speaker", "text", "movies", "expert_label"]
            ]
            conversation = []
            speaker = temp.iloc[0]["speaker"].lower()
            utterance = temp.iloc[0]["text"]
            for index, row in temp.iterrows():
                if index == 0:
                    continue

                row_speaker = row["speaker"].lower()
                row_text = row["text"]
                row_movies = row["movies"]

                is_recommendation = (
                    row_speaker == "recommender"
                    and not pd.isna(row_movies)
                )

                if is_recommendation:
                    conversation.append({
                        "speaker": speaker,
                        "utterance": utterance.replace(
                            "QUOTATION_MARK",
                            ""
                        ),
                        "recommend": False,
                    })
                    conversation.append({
                        "speaker": row_speaker,
                        "utterance": row_text.replace(
                            "QUOTATION_MARK",
                            ""
                        ),
                        "recommend": True,
                        "movies": row_movies
                    })
                    speaker = ""
                    utterance = ""
                else:
                    if speaker != row_speaker and utterance != "":
                        conversation.append({
                            "speaker": speaker,
                            "utterance": utterance.replace(
                                "QUOTATION_MARK",
                                ""
                            ),
                            "recommend": False
                        })
                        utterance = row_text
                        speaker = row_speaker
                    else:
                        utterance = f"{utterance}\n{row_text}"
                        speaker = row_speaker
            collection_conversations[dialogue_id] = conversation

        return collection_conversations

    def extract_dialogue_state(
        self,
        conv: list[dict[str, str]],
        latest_user_utterance: str
    ) -> dict[str, dict]:
        """
        Extracts the dialogue state from a conversation.

        Args:
            conv(list[dict[str, str]]): Conversation so far
            latest_user_utterance(str): Latest utterance by the user

        Returns:
            dict[str, dict]: The dialogue state extracted
        """
        graph = graphState(
            conversation=conv,
            latest_user_utterance=latest_user_utterance,
            system=self.agents
        )
        graph.invoke()
        return utils_functions.extract_dict_from_pydantic(
            graph.state["extraction_result"]
        )

    def create_recommendation_list(self, conv_id: str):
        """
        132
        """
        conv_original = self.conversations[conv_id][:10]
        conv_temp = []
        dialogue_state = []
        for turn in conv_original:
            if turn["recommend"]:
                pass
            else:
                conv_temp.append({
                    "speaker": turn["speaker"],
                    "utterance": turn["utterance"]
                })
                if turn["speaker"] == "seeker":
                    dialogue_state.append(
                        self.extract_dialogue_state(
                            conv=conv_temp[:-1],
                            latest_user_utterance=conv_temp[-1]["utterance"]
                        )
                    )
        return dialogue_state
