from backend.app import app
from backend.logger_config import setup_logger
import uuid
from rag import RAG

if __name__ == "__main__":
    setup_logger(logfile="app.log", max_length=120)

    # Generate session UUID
    SESSION_UUID = uuid.uuid4()

    rag = RAG(SESSION_UUID)

    # During setup/testing, disable the Flask reloader so handlers aren't duplicated
    app.run(debug=True, use_reloader=False)

