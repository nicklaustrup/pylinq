import logging
from utils.config import LOGGING_LEVEL

"""
Handles error logging and exception management across the application.
Provides utilities for clean error handling and debugging.
"""

# Configure logging
logging.basicConfig(
    level=LOGGING_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def log_error(message):
    """
    Logs an error message.

    Args:
        message (str): The error message to log.
    """
    logging.error(message)


def log_warning(message):
    """
    Logs a warning message.

    Args:
        message (str): The warning message to log.
    """
    logging.warning(message)


def log_info(message):
    """
    Logs an informational message.

    Args:
        message (str): The informational message to log.
    """
    logging.info(message)


def handle_exception(e, context=""):
    """
    Logs an exception with contextual information.

    Args:
        e (Exception): The exception object.
        context (str): Additional context where the error occurred.
    """
    logging.error(f"Exception occurred in {context}: {str(e)}")


# Example usage
if __name__ == "__main__":
    try:
        log_info("Starting the application...")
        raise ValueError("An example error.")
    except Exception as e:
        handle_exception(e, context="Main Application")
