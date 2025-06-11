from src.agents_src import graph_builder
from utils import utils_functions
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
import json


class DialogueStateTracker:
    def __init__(
        self,
        file_path: str,
        model_name: str
    ):
        self.file = json.loads(
            utils_functions.read_file(path=file_path)
        )
        self.conversations = self.create_conversations()
        self.system = graph_builder.agentSystem(model_name=model_name)

    def create_conversations(self) -> dict[str, dict[str, str]]:
        """
        Takes the file and extracts the conversation as well as the
        dialogue states.

        Args:
            None.
        Returns:
            dict: A dict with the dialogue, the state of it as well as an
            empty dict for the system to save the extracted values.
        """
        conversations = {}
        for key in self.file.keys():
            conversation = []
            dialog_act = []
            for index, log_dict in enumerate(self.file[key]["log"]):
                if index % 2 == 0:  # User
                    turn = "user"
                    dialog_act.append(log_dict["dialog_act"])
                else:
                    turn = "system"

                conversation.append({
                    turn: log_dict["text"]
                })
            conversations[key] = {
                "dialog_act": dialog_act,
                "conversation": conversation,
                "slot_values": {}
            }

        return conversations

    def extract_slot_values(self, file: str) -> None:
        """
        Takes the conversation and extracts the slot value pairs
        for each user utterance.

        Args:
            file (str): The name of the file for which to extract.

        Returns:
            None.
        """
        conversation = []
        for index, conversation_turn in enumerate(
            self.conversations[file]["conversation"]
        ):
            if index % 2 == 0:  # User
                print(conversation_turn["user"])
                graph = graph_builder.graphState(
                    conversation=conversation,
                    latest_user_utterance=conversation_turn["user"],
                    system=self.system
                )
                graph.invoke()
                self.conversations[file]["slot_values"][index] = (
                    graph.state["extraction_result"]
                )
                conversation.append(conversation_turn)
            else:  # System
                conversation.append(conversation_turn)
