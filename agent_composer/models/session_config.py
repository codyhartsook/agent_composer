import os
from pydantic import BaseModel
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from typing import Dict, Optional, List, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.language_models.chat_models import (
    BaseChatModel,
)
from langgraph.graph.graph import CompiledGraph
from langchain_core.runnables.base import RunnableSerializable
from dotenv import load_dotenv, find_dotenv


def load_env_file():
    # Try to find and load the default .env file first
    env_path = find_dotenv()
    if env_path != "":
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        # If the default .env file is not found, try to find and load .env.azure
        env_azure_path = find_dotenv(".env.azure")
        if env_azure_path:
            load_dotenv(dotenv_path=env_azure_path, override=True)
        else:
            raise FileNotFoundError("Neither .env nor .env.azure files were found")


class SessionConfig(BaseModel):
    chat_model: Optional[BaseChatModel] = None
    compiled_graph: Optional[CompiledGraph] = None
    writer_chain: Optional[RunnableSerializable] = None
    reflection_chain: Optional[RunnableSerializable] = None
    messages: List[BaseMessage] = []
    images: Dict[str, Any] = {}
    initialized: bool = False  # Flag to check if initialization has been done

    def __init__(self, *args, **kwargs):
        # Important to call super().__init__(**kwargs) to let Pydantic do its setup
        super().__init__(**kwargs)
        # Check if OPENAI_API_KEY or AZURE_OPENAI_API_KEY is set
        openai_api_key = os.getenv("OPENAI_API_KEY")
        azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")

        if openai_api_key:
            required_env_vars = [
                "OPENAI_API_KEY",
                "OPENAI_MODEL_NAME"
            ]

            missing_vars = [var for var in required_env_vars if not os.getenv(var)]
            if missing_vars:
                raise ValueError(f"The following environment variables are missing: {', '.join(missing_vars)}")
            self.chat_model = ChatOpenAI(api_key=openai_api_key, model=os.getenv("OPENAI_MODEL_NAME"))
        elif azure_openai_api_key:
            required_env_vars = [
                "AZURE_OPENAI_ENDPOINT",
                "AZURE_OPENAI_API_KEY",
                "AZURE_OPENAI_DEPLOYMENT",
                "AZURE_OPENAI_API_VERSION"
            ]

            missing_vars = [var for var in required_env_vars if not os.getenv(var)]
            if missing_vars:
                raise ValueError(f"The following environment variables are missing: {', '.join(missing_vars)}")

            # Handle Azure-specific initialization here
            self.chat_model = AzureChatOpenAI(azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                                              api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                              deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                                              openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                                              max_tokens=4096)
        else:
            raise ValueError("Neither OPENAI_API_KEY nor AZURE_OPENAI_API_KEY is set in the environment variables")

    def add_message(self, message: BaseMessage):
        """Append a message to the messages list."""
        self.messages.append(message)

    def add_messages(self, messages: List[BaseMessage]):
        """Extend the messages list with multiple messages."""
        self.messages.extend(messages)


load_env_file()
session_config = SessionConfig()
