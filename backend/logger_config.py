import logging
from pathlib import Path
from utils import MaxLengthFormatter

def setup_logger(logfile="app.log", max_length=120, level=logging.DEBUG):
    root = logging.getLogger()       # use root so all child loggers propagate here
    root.setLevel(level)

    # Important when running Flask with reloader: don't add duplicates
    if any(isinstance(h, logging.FileHandler) for h in root.handlers):
        return root

    fh = logging.FileHandler(Path(logfile), encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(MaxLengthFormatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        max_length=max_length
    ))
    root.addHandler(fh)

    # Optional: stop libraries from adding their own handlers
    logging.captureWarnings(True)

    return root