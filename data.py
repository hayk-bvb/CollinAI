import os
from langchain_openai import ChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
import asyncio
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import AzureOpenAIEmbeddings
from utils import check_whitespace_or_invalid_type, clean_pages
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
load_dotenv()


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = CURRENT_DIR + "/20240601_Regulations_CLFS_2024_EN.pdf"



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
        
        self.embeddings = AzureOpenAIEmbeddings(
            model="text-embedding-ada-002"
        )

    def get_embeddings(self, raw_pages):
        check_whitespace_or_invalid_type(raw_pages)

        cleaned_pages = clean_pages(raw_pages)
        documents = []
        for page in cleaned_pages:
            if page.page_content and isinstance(page.page_content, str):
                documents.append(Document(
                    id=str(page.metadata['page']),
                    page_content=page.page_content,
                    metadata=page.metadata
                ))
            else:
                print(f"Skipping invalid page: {page.metadata.get('page')} (bad content)")

        print(f"Chunking documents.")
        chunked_docs = self.chunk_documents(documents)


        print(f"Prepared {len(documents)} documents for FAISS embedding.")

        vector_store = FAISS.from_documents(chunked_docs, self.embeddings)
        vector_store.save_local("faiss_index/")
    
    def chunk_documents(self, documents):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )
        return splitter.split_documents(documents)

        
    def search(self, query):
        vector_store = FAISS.load_local("faiss_index/", self.embeddings, allow_dangerous_deserialization=True)
        
        docs = vector_store.similarity_search(query, k=2)
        for doc in docs:
            print(f'Page {doc.metadata["page"]}: {doc.page_content[:300]}\n')

    def invoke():
        """"""
        pass


    async def load_pdf_async(self, file_path):
        loader = PyPDFLoader(file_path)
        pages = []
        async for page in loader.alazy_load():
            pages.append(page)
        return pages



my_provider = Azure()

raw_pages = asyncio.run(my_provider.load_pdf_async(FILE_PATH))
# print(pages[0].metadata)

# cosine = my_provider.get_embeddings(raw_pages=raw_pages)
cosine = my_provider.search("requirements for training facilities")
print(cosine)

    