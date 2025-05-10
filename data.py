import os
from langchain_openai import ChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader

FILE_PATH = 

class Provider:
    """An abstraction for a Langchain Provider"""
    def __init__(self):
        pass


class Azure(Provider):
    """Azure implementation with Langchain"""

    def __init__(self):
        super().__init__()
        # Azure OpenAI credentials
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    def get_embeddings():
        """"""
        pass

    def invoke():
        """"""
        pass




loader = PyPDFLoader(file_path)
pages = []
async for page in loader.alazy_load():
    pages.append(page)

