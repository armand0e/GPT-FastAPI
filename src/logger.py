import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Determine the absolute log directory
BASE_DIR = Path(__file__).resolve().parent  # Script's directory
LOG_DIR = BASE_DIR / "logs"

# Ensure the logs directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "system.log"

def get_logger():
    """Returns a configured logger that writes to a rotating log file and console."""
    logger = logging.getLogger("system")
    
    if not logger.hasHandlers():  # Avoid duplicate handlers
        # File Handler with rotation (5MB max, keeps last 5 logs)
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8")
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)

        # Console Handler (for real-time debugging)
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)

    return logger