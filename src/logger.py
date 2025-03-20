import logging
from collections import deque
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
import sys
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

def setup_logger(name: str, log_file: str, level: str='INFO'):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        log_queue = deque(maxlen=20)

        class MemoryHandler(logging.Handler):

            def emit(self, record):
                log_queue.append(self.format(record))
        file_path = LOG_DIR / log_file
        file_handler = TimedRotatingFileHandler(str(file_path), when='midnight', interval=1, backupCount=1, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        memory_handler = MemoryHandler()
        memory_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.addHandler(memory_handler)
        logger.setLevel(level)
        logger.propagate = False
    return logger

system_logger = setup_logger('system', 'system.log')