from abc import ABC
from backend.llm import OpenAIModel
from backend.database import RedisClient
from backend.graph import Graph
from pprint import pprint
import logging
from backend.data import Azure

logging.getLogger(__name__)

# Initialize the database
db = RedisClient(cold_start=True)


class RAG(ABC):
    """This class with be responsible for a RAG pipeline. """

    def __init__(self, session_id):
        super().__init__()

        # Instantiate the model
        self.__model = OpenAIModel()

        self.__provider = Azure()
        
        # Instantiate the graph
        self.__graph = Graph(self.__provider, self.__model.get_llm(), db, session_id)

    def ask(self, query: str, verbose: bool = False):
        """Ask the model a question. """
        return self.__graph.run(query=query, verbose=verbose)
    


question = "can any club sign a player?"


if __name__ == "__main__":
    rag = RAG("test session")
    pprint(rag.ask(query=question))
