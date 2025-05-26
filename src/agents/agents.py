from langgraph.graph import Command
from agents.agent_data_definitions import MetaExpertState


def meta_expert_agent(state: MetaExpertState) -> Command:
    # Check if domains is empty or missing
    if not state.get("domains"):
        # Route to fallback agent (replace "fallback_agent" with your agent's name)
        return Command(goto="domain_extractor_agent")

    # Normal processing here
    # ...

    # Continue or end as appropriate
    return Command(goto="meta_expert_agent")  # or Command(goto=END)


def domain_extractor_agent(state: MetaExpertState) -> Command:
     