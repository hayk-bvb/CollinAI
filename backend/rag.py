from abc import ABC
from llm import OpenAIModel
from database import RedisClient
from graph import Graph
from pprint import pprint
import logging

logging.getLogger(__name__)

# Initialize the database
# TODO: Figure out when you need the cold start as opposed to when you dont
db = RedisClient(cold_start=True)

# Initialize the logging instance


class RAG(ABC):
    """This class with be responsible for a RAG pipeline. """

    def __init__(self, session_id):
        super().__init__()


        # Instantiate the model
        self.__model = OpenAIModel()
        
        # Instantiate the graph
        self.__graph = Graph(self.__model.get_llm(), db, session_id)

    def ask(self, query: str, verbose: bool = False):
        """Ask the model a question. """
        return self.__graph.run(query=query, verbose=verbose)
    


question = "can any club sign a player?"


if __name__ == "__main__":
    # TODO: Need to properly format answered and verbose type of answer where you can see the context that was fed into the AI.
    rag = RAG("test session")
    pprint(rag.ask(query=question))
