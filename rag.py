from abc import ABC
from llm import OpenAIModel

class RAG(ABC):
    """This class with be responsible for a RAG pipeline. """

    def __init__(self):
        super().__init__()

        # Instantiate model
        self.model = OpenAIModel()

    def ask(self, query: str):
        """Ask the model a question. """
        return self.model.invoke(question=query)