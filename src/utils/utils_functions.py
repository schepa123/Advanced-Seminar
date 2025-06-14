import os
import json
from uuid import uuid4
import re
from langchain_core.prompts import ChatPromptTemplate
import sys
import yaml
import pandas as pd
from textwrap import dedent
from langchain_core.prompts.prompt import PromptTemplate

sys.path.append("..")
from agents_src_woz.agent_data_definitions import MetaExpertState
from langchain_core.documents import Document


def get_cwd() -> str:
    """
    Returns the current working directory.

    Args:
        None.

    Returns:
        str: The current working directory.
    """
    return os.path.realpath(os.path.join(
        os.getcwd(), os.path.dirname(__file__)
    ))


def return_root_dir() -> str:
    """
    Returns the root directory of the project.

    Args:
        None.

    Returns:
        str: The root directory of the project.
    """
    path = get_cwd()
    return os.path.dirname(
        os.path.dirname(path)
    )


def read_file(path: str) -> str:
    """
    Reads file from path.

    Args:
        path (str): Path to the file.

    Returns:
        str: The content of the file.
    """
    with open(path, "r") as f:
        return f.read()


def read_yml(path: str) -> dict[str, str]:
    """
    Reads and returns yml file.

    Args:
        path (str): Path to the yml file

    Returns:
        dict[str, str]: Yml file as dict
    """

    with open(path) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return {}


def return_prompt(prompt_name: str, dataset: str = "inspire") -> PromptTemplate:
    """
    Returns prompt based on the specifed prompt
    name.

    Args:
        prompt_name (str): The name of the prompt.

    Returns:
        str: The prompt.
    """
    return PromptTemplate.from_file(
        os.path.join(
            return_root_dir(),
            "prompts",
            dataset,
            f"{prompt_name}.md"
        )
    )


def replace_single_curly_brackets(string_value: str) -> str:
    """
    Replaces every instance of single curly brackets with two
    curly brackets.

    Args:
        string_value (str): String to modify.

    Returns:
        str: Modified string.
    """
    text = re.sub(r'(?<!\{)\{(?!\{)', r'{{', string_value)
    # 2) Replace every single “}” (not part of “}}”) → “}}”
    text = re.sub(r'(?<!\})\}(?!\})', r'}}', string_value)
    return text


def return_slots_present(state: MetaExpertState) -> dict[str, str]:
    """
    Returns the slot-value definitions for present domains.

    Args:
        state (MetaExpertState): Current state of the system.

    Returns:
        dict[str, str]: The slot value definitions.
    """
    slot_dict = read_yml(path=os.path.join(
        return_root_dir(),
        "src",
        "agents_src",
        "domain_slots.yml"
    ))
    return {
        key: value for key, value in slot_dict.items()
        if key in state.domains
        # if key in state["domains"]
    }


def build_last_utterance_prompt(state: MetaExpertState) -> dict[str, str]:
    """
    Builds the prompt combining the prior conversation and the
    latest_user_utterance.

    Args:
        state (MetaExpertState): Current state of the system.

    Returns:
        str: The created prompt.
    """
    return {
        "prior_conversation": state.conversation,
        "latest_user_utterance": state.latest_user_utterance
    }


def build_slot_extraction_prompt_old(state: MetaExpertState) -> dict[str, str]:
    """
    Build the slot extraction prompt by combining the slots definition
    present in the latest user utterance with the last utterance prompt

    Args:
        state (MetaExpertState): Current state of the system.

    Returns:
        str: The created prompt.
    """
    user_prompt_dict = {
        "domain": state.domains,
        "slot_value_pair": replace_single_curly_brackets(
            json.dumps(return_slots_present(state))
        ),
        "prior_conversation": replace_single_curly_brackets(
            json.dumps(state.conversation)
        ),
        "latest_user_utterance": state.latest_user_utterance
    }

    return user_prompt_dict


def build_slot_extraction_prompt(
    # state: MetaExpertState,
    slots: dict[str, str],
    latest_user_utterance: str,
    conv
) -> dict[str, str]:
    """
    Build the slot extraction prompt by combining the slots definition
    present in the latest user utterance with the last utterance prompt

    Args:
        state (MetaExpertState): Current state of the system.

    Returns:
        str: The created prompt.
    """
    user_prompt_dict = {
        "slot_value_pair": replace_single_curly_brackets(
            json.dumps(slots)
        ),
        "prior_conversation": replace_single_curly_brackets(
            # json.dumps(state.conversation)
            json.dumps(conv)
        ),
        #"latest_user_utterance": state.latest_user_utterance
        "latest_user_utterance": latest_user_utterance
    }

    return user_prompt_dict


def build_verification_prompt(
    # state: MetaExpertState,
    slots: dict[str, str],
    latest_user_utterance: str,
    conv,
    extraction_results
    ) -> dict[str, str]:
    """
    123
    """
    user_prompt_dict = {
        "slot_value_pair_description": replace_single_curly_brackets(
            json.dumps(slots)
        ),
        "prior_conversation": replace_single_curly_brackets(
            # json.dumps(state.conversation)
            json.dumps(conv)
        ),
        "latest_user_utterance": latest_user_utterance,
        "extraction_results": extraction_results
    }

    return user_prompt_dict


def build_verification_prompt_old(state: MetaExpertState) -> dict[str, str]:
    """
    Build the verification prompt by combining the slots definition
    present in the latest user utterance with the extraction results.

    Args:
        state (MetaExpertState): Current state of the system.

    Returns:
        str: The created prompt.
    """
    return {
        "domain": state.domains,
        #"domain": state["domains"],
        "slot_value_pair_description": replace_single_curly_brackets(
            json.dumps(return_slots_present(state))
        ),
        "prior_conversation": replace_single_curly_brackets(
            json.dumps(state.conversation)
            #json.dumps(state["conversation"])
        ),
        #"latest_user_utterance": state["latest_user_utterance"],
        "latest_user_utterance": state.latest_user_utterance,
        #"extraction_results": state["extraction_result"]
        "extraction_results": state.extraction_result
    }


def create_issue_solving_dict(state: MetaExpertState) -> dict[str, str]:
    """
    Creates the dict for the issue solving agent by select only wrong entries.

    Args:
        state (MetaExpertState): Current state of the system.

    Returns:
        dict[str, str]: the dict for the issue solving agent.
    """
    wrong_entries = {}
    for key, value in state.last_verification_results.items():
    # for key, value in dict(state["last_verification_results"].root).items():
        temp_dict = dict(value)
        if not temp_dict["boolean"]:
            temp_dict.pop("boolean", None)
            wrong_entries[key] = temp_dict

    return wrong_entries


def build_issue_solving_prompt(state: MetaExpertState) -> dict[str, str]:
    """
    Build the issue solving prompt by combining the slots definition
    present in the latest user utterance with the verification results.

    Args:
        state (MetaExpertState): Current state of the system.

    Returns:
        str: The created prompt.
    """
    test = {
        "domain": state.domains,
        # "domain": state["domains"],
        "slot_value_pair_description": replace_single_curly_brackets(
            json.dumps(return_slots_present(state))
        ),
        "prior_conversation": replace_single_curly_brackets(
            json.dumps(state.conversation)
            # json.dumps(state["conversation"])
        ),
        # "latest_user_utterance": state["latest_user_utterance"],
        "latest_user_utterance": state.latest_user_utterance,
        "wrong_results": replace_single_curly_brackets(
            json.dumps(create_issue_solving_dict(state))
        )
    }
    return test


def fix_common_spelling_mistakes(domains: list[str]) -> list[str]:
    """
    Makes words lower cases and fixes spelling mistakes.

    Args:
        domains list(str): List of domains present.

    Returns:
        list(str): List of domains present with fixed
        spelling
    """
    domains = [domain.lower() for domain in domains]
    spelling_fix = {
        "hotels": "hotel",
        "trains": "train",
        "attractions": "attractions",
        "restaurants": "restaurant",
        "taxi": "taxis",
    }

    return [
        spelling_fix[domain] if domain in spelling_fix
        else domain for domain in domains
    ]


