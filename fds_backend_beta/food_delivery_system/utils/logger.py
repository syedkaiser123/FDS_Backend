import logging
import os
from logging.handlers import RotatingFileHandler

# Ensure logs directory exists
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "app.log")


def get_logger(name: str):
    """
    Creates and returns a custom logger.
    """
    logger = logging.getLogger(name)

    if not logger.hasHandlers():  # Prevent duplicate handlers
        logger.setLevel(logging.DEBUG)  # Set log level

        # Format logs with timestamps
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # File handler (Rotates after 5MB, keeps last 3 logs)
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
        file_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


# Usage example
logger = get_logger(__name__)
logger.info("Custom logger initialized successfully")


