from langchain_openai import ChatOpenAI
import logging
from cascade_node_sdk.agent import AgentProxy
import operator
from typing import Sequence, TypedDict, Union, Annotated
from langchain_core.messages import BaseMessage
from langchain_core.agents import AgentAction, AgentFinish
from os import environ
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

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

def chatbot(state: AgentState):
    logging.info("test")
    logging.info(environ["OPENAI_API_KEY"])
    llm = ChatOpenAI(model="gpt-4")
    return {"messages": [llm.invoke(state["messages"])]}

if __name__ == "__main__":
    agent = AgentProxy(
        config_path="catalog-info.yaml",
    )
    agent.run_agent(entrypoint_func=chatbot)