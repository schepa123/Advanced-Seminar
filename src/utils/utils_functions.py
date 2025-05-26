import os
from langchain_core.prompts import ChatPromptTemplate


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


def return_prompt(prompt_name: str) -> str:
    """
    Returns prompt based on the specifed prompt
    name.

    Args:
        prompt_name (str): The name of the prompt.

    Returns:
        str: The prompt.
    """

    return read_file(os.path.join(
        return_root_dir(),
        "prompts",
        f"{prompt_name}.md"
    ))
