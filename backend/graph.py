from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import MessagesState, StateGraph
from langgraph.graph import END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import Tool
from data import Azure
import uuid
import logging

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')


class Graph:
    """This class is responsible for representing the Langgraph implementation of our application."""

    def __init__(self, llm, db, session_id):
        self.__llm = llm
        self.db = db
        self.session_id = session_id

        self.__provider = Azure()
        self._retriever = self.__provider.load_vector_store("faiss_index/").as_retriever()

        self.graph_builder = StateGraph(MessagesState)

        self.retrieve_tool = Tool(
            name="retrieve",
            func=self._retrieve_function,
            description=(
                "Always use this to retrieve documents before answering legal football (soccer) questions."
            )
        )

        # Step 2: Execute the retrieval
        self.tools = ToolNode([self.retrieve_tool])

        self.checkpointer = self.db.get_checkpointer()
        self.config = {
            "configurable": {
                "thread_id": self.create_thread_for_session(session_id)  # new ID every time
            }
        }

        self.graph = self.setup_graph()

    def create_thread_for_session(self, session_id: str) -> str:
        thread_id = str(uuid.uuid4())
        self.db.get_client().sadd(f"session:{session_id}:threads", thread_id)
        return thread_id


    def _retrieve_function(self, query: str):
        logger.info("Retreiving info: ...")
        retrieved_docs = self._retriever.invoke(query)
        logger.debug(f"Num of retrieved docs: {len(retrieved_docs)}")
        for doc in retrieved_docs:
            logger.debug(doc.page_content)
            
                
        # print(retrieved_docs)
        serialized = "\n\n".join(
            (f"Source {doc.metadata} \n Content: {doc.page_content}" for doc in retrieved_docs)
        )
        return serialized, retrieved_docs
    
    # Step 1: Generate an AIMessage that may include a tool-call to be sent.
    def query_or_respond(self, state: MessagesState):
        """Generate tool call for retrieval or respond."""
        llm_with_tools = self.__llm.bind_tools([self.retrieve_tool])

        # Inject system message if not already present
        system_prompt = SystemMessage(
            content=(
                "You are Collin, a legal expert in football (soccer) law. "
                "For **every** user question, you must first use the `retrieve` tool "
                "to look up relevant documents before providing an answer. "
                "Do not answer directly without calling the tool first. "
                "Only after retrieving, should you respond."
            )
        )

        # Ensure we only inject it once
        new_messages = [system_prompt] + [
            msg for msg in state["messages"]
            if msg.type != "system"
        ]

        response = llm_with_tools.invoke(new_messages)
        logger.debug(f"Tools calls: {response.tool_calls}")
        return {"messages": [response]}
    
    # Step 3: Generate a response using the retrieved content.
    def generate(self, state: MessagesState):
        """Generate answer."""
        # Get generated ToolMessages
        recent_tool_messages = []
        for message in reversed(state["messages"]):
            if message.type == "tool":
                recent_tool_messages.append(message)
            else:
                break
        tool_messages = recent_tool_messages[::-1]

        # Format into prompt
        docs_content = "\n\n".join(doc.content for doc in tool_messages)
        system_message_content = (
            "You are Collin, a football (soccer) legal expert. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you don't know. "
            "\n\n"
            f"{docs_content}"
        )
        conversation_messages = [
            message
            for message in state["messages"]
            if message.type in ("human", "system")
            or (message.type == "ai" and not message.tool_calls)
        ]
        prompt = [SystemMessage(system_message_content)] + conversation_messages

        # logger.debug("====== Final Prompt to LLM ======")
        # for msg in prompt:
        #     logger.debug(f"{msg.type.upper()}: {msg.content}")
        # logger.debug("=================================")

        response = self.__llm.invoke(prompt)
        
        return {"messages": response}

    
    def setup_graph(self):
        """Make the langraph."""
        self.graph_builder.add_node(self.query_or_respond)
        self.graph_builder.add_node(self.tools)
        self.graph_builder.add_node(self.generate)

        self.graph_builder.set_entry_point("query_or_respond")
        self.graph_builder.add_conditional_edges(
            "query_or_respond",
            tools_condition,
            {END: END, "tools": "tools"},
        )
        self.graph_builder.add_edge("tools", "generate")
        self.graph_builder.add_edge("generate", END)

        graph = self.graph_builder.compile(self.checkpointer)
        return graph
    
    
    def step(self, query: str):
        print("=== Debug Step-by-Step ===")
        for step in self.graph.stream({"messages": [HumanMessage(content=query)]},
                                      self.config,
                                      stream_mode="values"):
            msg = step["messages"][-1]
            print(f"[{msg.type.upper()}] {msg.content}")

    def run(self, query: str) -> str:
        result = self.graph.invoke(
            {"messages": [HumanMessage(content=query)]},
            self.config
        )
        return result["messages"][-1].content