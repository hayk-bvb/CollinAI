from abc import ABC
from llm import OpenAIModel
from database import RedisClient
from graph import Graph
from logger_config import setup_logger



# Initialize the database
# TODO: Figure out when you need the cold start as opposed to when you dont
db = RedisClient(cold_start=True)

# Initialize the logging instance


class RAG(ABC):
    """This class with be responsible for a RAG pipeline. """

    def __init__(self, session_id):
        super().__init__()
        setup_logger()

        # Instantiate the model
        self.__model = OpenAIModel()
        
        # Instantiate the graph
        self.__graph = Graph(self.__model.get_llm(), db, session_id)

    def ask(self, query: str):
        """Ask the model a question. """
        return self.__graph.run(query=query)
    


question = "yes"


if __name__ == "__main__":
    # TODO: Need to properly format answered and verbose type of answer where you can see the context that was fed into the AI.
    rag = RAG()
    print(rag.ask(query=question))
