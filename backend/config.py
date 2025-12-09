import logging
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv

load_dotenv()

LOG_DIR = os.getenv("logs")
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logging():
    # Root Logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] — %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    # ----------- File: app.log (general logs) -----------
    file_handler = RotatingFileHandler(
        f"{LOG_DIR}/app.log", maxBytes=5_000_000, backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # ----------- File: error.log -----------
    error_handler = RotatingFileHandler(
        f"{LOG_DIR}/error.log", maxBytes=5_000_000, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logging.info("Logging initialized.")
