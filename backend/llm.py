import os
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import AzureChatOpenAI
from abc import ABC, abstractmethod


# ABSTRACT METHOD
class LLM(ABC):
    """This class is responsible for communicating with LLM endpoint with appropriate params."""

    def __init__(self):
        pass
    
    @abstractmethod
    def get_llm(self):
        pass



class OpenAIModel(LLM):
    """Child of LLM and extends with using OpenAI LLM Endpoint. """

    def __init__(self):
        super().__init__()

        self._api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self._endpoint = os.getenv("AZURE_OPENAI_COMPLETION_ENDPOINT")
        self._model = "o3-mini"

        self.__llm = AzureChatOpenAI(
                    deployment_name=self._model,
                    openai_api_key=self._api_key,
                    azure_endpoint=self._endpoint,
                    openai_api_version="2025-01-01-preview"
                )

    
    def get_llm(self):
        """A getter method for the LLM we are using."""
        return self.__llm









