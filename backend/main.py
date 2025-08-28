from routing.routes import app  # Flask instance
from logger_config import setup_logger

if __name__ == "__main__":
    setup_logger(logfile="app.log", max_length=50)

    # During setup/testing, disable the Flask reloader so handlers aren't duplicated
    app.run(debug=True, use_reloader=False)