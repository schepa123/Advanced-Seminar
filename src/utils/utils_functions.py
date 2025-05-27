import os
from langchain_core.prompts import ChatPromptTemplate
import sys
import yaml
sys.path.append("..")
from agents_src.agent_data_definitions import MetaExpertState
from textwrap import dedent
from langchain_core.prompts.prompt import PromptTemplate


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


def return_prompt(prompt_name: str) -> PromptTemplate:
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
            f"{prompt_name}.md"
        )
    )


def build_last_utterance_prompt(state: MetaExpertState) -> str:
    """
    Builds the prompt combining the prior conversation and the
    latest_user_utterance.

    Args:
        state (MetaExpertState): Current state of the system.

    Returns:
        str: The created prompt.
    """
    return dedent(f"""
    <prior_conversation>{state.get('conversation')}</prior_conversation>
    <latest_user_utterance>{state.get('latest_user_utterance')}</latest_user_utterance>
    """)


def build_slot_extraction_prompt(state: MetaExpertState) -> str:
    """
    Build the slot extraction prompt by combining the slots definition
    present in the latest user utterance with the last utterance prompt

    Args:
        state (MetaExpertState): Current state of the system.

    Returns:
        str: The created prompt.
    """
    slot_dict = read_yml(path=os.path.join(
        return_root_dir(),
        "src",
        "agents_src",
        "domain_slots.yml"
    ))
    domains_present = {
        key: value for key, value in slot_dict.items()
        if key in state.get('domains')
    }
    print(1)
    last_utterance_prompt = build_last_utterance_prompt(state)
    return dedent(f"""
        <slot_value_pair>
        {domains_present}
        </slot_value_pair>
        {last_utterance_prompt}
    """)


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

    return [spelling_fix[domain] for domain in domains]