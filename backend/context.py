from backend.rag import RAG
import uuid

SESSION_UUID = str(uuid.uuid4())
rag = RAG(SESSION_UUID)