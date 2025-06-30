import os
from langchain_openai import ChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
import asyncio
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from abc import ABC, abstractmethod
from utils import Utils
import logging

logger = logging.getLogger(__name__)
load_dotenv()


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = CURRENT_DIR + "/20240601_Regulations_CLFS_2024_EN.pdf"

utils = Utils()

class Provider(ABC):
    """An abstraction for a Langchain Provider"""
    def __init__(self):
        pass

    @abstractmethod
    def get_embeddings(self):
        pass

    @abstractmethod
    def generate_embeddings(self):
        pass
    
    @abstractmethod
    def search(self):
        pass


class Azure(Provider):
    """Azure implementation with Langchain"""

    def __init__(self):
        super().__init__()
        # Azure OpenAI credentials
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_EMBEDDINGS_ENDPOINT")
        
        self.embeddings = AzureOpenAIEmbeddings(
            model="text-embedding-ada-002",
            azure_endpoint=self.endpoint
        )
    
    def get_embeddings(self):
        return self.embeddings

    def generate_embeddings(self, raw_pages) -> None:
        """Take raw input pages, put into documents and chunk them. Then use OpenAI Embeddings to create and save index."""
        
        utils.check_whitespace_or_invalid_type(raw_pages)

        cleaned_pages = utils.clean_pages(raw_pages)
        documents = []
        for page in cleaned_pages:
            documents.append(Document(
                id=str(page.metadata['page']),
                page_content=page.page_content,
                metadata=page.metadata
            ))

        chunked_docs = self.chunk_documents(documents)

        vector_store = FAISS.from_documents(chunked_docs, self.embeddings)
        vector_store.save_local("faiss_index/")
    
    def chunk_documents(self, documents):
        """Take documents and chunk them uniformly. """
        
        logger.info(f"Chunking documents.")
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )
        chunks = splitter.split_documents(documents)
        logger.info(f"Prepared {len(chunks)} chunks for FAISS embedding.")
        return chunks

        
    def search(self, query: str, k: int, verbose:bool=False):
        vector_store = self.load_vector_store("faiss_index/")
        
        docs = vector_store.similarity_search(query, k=k)
        if verbose:
            for doc in docs:
                print(f'Page {doc.metadata["page"]}: {doc.page_content}\n')
        return docs

    def load_vector_store(self, path: str):
        """Load the vector store using the given path. """

        vector_store = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
        return vector_store


    async def load_pdf(self, file_path):
        loader = PyPDFLoader(file_path)
        pages = []
        async for page in loader.alazy_load():
            pages.append(page)
        return pages



my_provider = Azure()

raw_pages = asyncio.run(my_provider.load_pdf(FILE_PATH))
# print(pages[0].metadata)

# cosine = my_provider.generate_embeddings(raw_pages=raw_pages)
# cosine = my_provider.search("requirements for training facilities", 3)
# print(cosine)

    