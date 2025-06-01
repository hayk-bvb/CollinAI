import os
from dotenv import load_dotenv
load_dotenv()
from data import Azure
from langchain_openai import AzureChatOpenAI
from langchain.memory import ConversationBufferMemory
from pprint import pprint
from abc import ABC, abstractmethod
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
import json
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_core.runnables import RunnableSequence
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import MessagesState, StateGraph
from langgraph.graph import END
from langgraph.prebuilt import ToolNode, tools_condition


class LLM(ABC):
    """This class is responsible for communicating with LLM endpoint with appropriate params."""

    def __init__(self):
        pass



class OpenAIModel(LLM):
    """Child of LLM and extends with using OpenAI LLM Endpoint. """

    def __init__(self):
        super().__init__()

        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_COMPLETION_ENDPOINT")
        self.model = "o3-mini"
        
        self.provider = Azure()
        self.retriever = self.provider.load_vector_store("faiss_index/").as_retriever()

        self.llm = AzureChatOpenAI(
                    deployment_name=self.model,
                    openai_api_key=self.api_key,
                    azure_endpoint=self.endpoint,
                    openai_api_version="2025-01-01-preview"
                )

        self.graph_builder = StateGraph(MessagesState)
        # Step 2: Execute the retrieval
        self.tools = ToolNode([self.retrieve])


    
    @tool(response_format="content_and_artifact")
    def retrieve(self, query: str):
        """Retrieve information related to a query."""
        retrieved_docs = self.provider(query, k=3)
        serialized = "\n\n".join(
            (f"Source {doc.metadata}\n" f"Content: {doc.page_content}"
             for doc in retrieved_docs)
        )
        return serialized, retrieved_docs
    
    # Step 1: Generate an AIMessage that may include a tool-call to be sent.
    def query_or_respond(self, state: MessagesState):
        """Generate tool call for retrieval or respond."""
        llm_with_tools = self.llm.bind_tools([self.retrieve])
        response = llm_with_tools.invoke(state["messages"])
        # MessagesState appends messages to the state instead of overwriting
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
            "You are a football (soccer) legal expert, your name is Collin. "
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

        response = self.llm.invoke(prompt)
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

        graph = self.graph_builder.compile()
        return graph
    


# model = OpenAIModel()
# # ans = model.invoke("What does Article 28 say about equal rights?")
# ans = model.invoke("What is your name?")
# pprint(ans)

# Test
model = OpenAIModel()
input_message = "What does Article 28 say about equal rights?"
graph = model.setup_graph()


for step in graph.stream(
    {"messages": [{"role": "user", "content": input_message}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()



