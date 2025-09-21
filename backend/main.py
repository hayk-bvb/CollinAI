from backend.app import app
from backend.logger_config import setup_logger
import backend.routing.routes

if __name__ == "__main__":
    setup_logger(logfile="app.log", max_length=120)

    # During setup/testing, disable the Flask reloader so handlers aren't duplicated
    app.run(host="0.0.0.0", debug=True, use_reloader=False)

