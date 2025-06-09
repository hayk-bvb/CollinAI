from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import MessagesState, StateGraph
from langgraph.graph import END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import Tool
from data import Azure


class Graph:
    """This class is responsible for representing the Langgraph implementation of our application."""

    def __init__(self, llm, db):
        self.__llm = llm
        self.db = db

        self.__provider = Azure()
        self._retriever = self.__provider.load_vector_store("faiss_index/").as_retriever()

        self.graph_builder = StateGraph(MessagesState)

        self.retrieve_tool = Tool(
            name="retrieve",
            func=self._retrieve_function,
            description=(
                "Use this tool to retrieve documents related to legal questions in football (soccer), "
                "including references to articles, statutes, or equal rights."
            )
        )

        # Step 2: Execute the retrieval
        self.tools = ToolNode([self.retrieve_tool])

        self.checkpointer = self.db.get_checkpointer()
        self.config = {
            "configurable": {
                "thread_id": "1"
            }
        }

        self.graph = self.setup_graph()


    def _retrieve_function(self, query: str):
        retrieved_docs = self._retriever.invoke(query)
        serialized = "\n\n".join(
            (f"Source {doc.metadata}\nContent: {doc.page_content}" for doc in retrieved_docs)
        )
        return serialized, retrieved_docs
    
    # Step 1: Generate an AIMessage that may include a tool-call to be sent.
    def query_or_respond(self, state: MessagesState):
        """Generate tool call for retrieval or respond."""
        llm_with_tools = self.__llm.bind_tools([self.retrieve_tool])

        # Inject system message if not already present
        system_prompt = SystemMessage(
            content=(
                "You are Collin, a legal expert in football (soccer) law."
                "When you are answering a question relating to football, use the `retrieve` tool to look up relevant documents. "
                "Your responses should be concise and precise."
            )
        )

        # Ensure we only inject it once
        new_messages = [system_prompt] + [
            msg for msg in state["messages"]
            if msg.type != "system"
        ]

        response = llm_with_tools.invoke(new_messages)

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
            " Try to keep the answer concise, around 10 sentences should be your maximum."
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

        print("====== Final Prompt to LLM ======")
        for msg in prompt:
            print(f"{msg.type.upper()}: {msg.content}")
        print("=================================")

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
    
    
    def step(self, query):
        """..."""
        for step in self.graph.stream({"messages": [HumanMessage(content=query)]},
                                 self.config,
                                 stream_mode="values"):
            
            step["messages"][-1].pretty_print()