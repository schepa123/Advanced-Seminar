from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages

import yaml
import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


def load_yaml(path: str) -> dict[str, str]:
    """
    Loads yaml file from path.

    Args:
        path (str): Path to the yaml file.

    Returns:
        Yaml file.
    """
    with open(path) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return {}


def return_slots(domains: list[str]) -> dict[str, str]:
    """
    It takes a list of domains and returns a dictionary containing
    all the slots and their definitions for each provided domain.

    Args:
        domains (list[str]): List of domains.

    Return:
        dict[str, str]: Domains with their slots and slot
        definition.
    """
    __location__ = os.path.realpath(os.path.join(
        os.getcwd(), os.path.dirname(__file__)
    ))
    slot_yml = load_yaml(
        path=os.path.join(__location__, "domain_slots.yml")
    )
    slot_defintion = {}

    for domain in domains:
        slot_defintion[domain.lower()] = slot_yml[domain.lower()]

    return slot_defintion
