import pandas as pd
import os
import json
from uuid import uuid4


class inspiredDataset:
    def __init__(self, path: str) -> None:
        self.path = path
        self.conversations = self.create_conversation_data()

    def create_conversation_data(self) -> dict[str, dict[str, str]]:
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
