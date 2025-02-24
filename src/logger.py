import os
import logging

# Determine the absolute log directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Script's directory
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Ensure the logs directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Logger configuration
def get_logger():
    """Returns a configured logger that writes to a specified log file."""
    log_path = os.path.join(LOG_DIR, "system.log")

    logger = logging.getLogger("system.log")
    if not logger.hasHandlers():  # Avoid duplicate handlers
        handler = logging.FileHandler(log_path, encoding="utf-8")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger
