"""
Logging configuration module.

Sets up global logging for the application.
Logs INFO and ERROR level messages to 'activity.log'.
"""

import logging

LOG_FILE = "activity.log"

def configure_logging() -> None:
    """
    Configure global logging settings.

    Logs are appended to the log file with timestamp, level, and message.
    """
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        filemode="a"
    )
