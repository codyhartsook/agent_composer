import operator
from typing import Sequence, List, Any, Dict, TypedDict, Union, Annotated
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.agents import AgentAction, AgentFinish


class AgentState(TypedDict):
    # The input string
    input: str
    # The list of previous messages in the conversation
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The outcome of a given call to the agent
    # Needs `None` as a valid type, since this is what this will start as
    agent_outcome: Union[AgentAction, AgentFinish, None]
    # List of actions and corresponding observations
    # Here we annotate this with `operator.add` to indicate that operations to
    # this state should be ADDED to the existing values (not overwrite it)
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]
    last_agent: str