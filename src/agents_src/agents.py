from langgraph.graph import Command
import agent_tools
import agent_data_definitions  
from utils import utils_functions
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent



def create_all_agents():
    model = init_chat_model(
        "openai:o4-mini-2025-04-16",
    )
    domain_extractor = create_react_agent(
        model=model,
        tools=[agent_tools.return_slots],
        prompt=utils_functions.return_prompt("detect_domain"),
        response_format=agent_data_definitions.DomainResponse
    )

    return domain_extractor