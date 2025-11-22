"""
Logging configuration for the query expansion project.
"""

import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(
    log_level=logging.INFO, log_to_file=True, log_dir="logs", log_file=None
):
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (default: INFO)
        log_to_file: Whether to log to file (default: True)
        log_dir: Directory for log files (default: 'logs')
        log_file: Specific log file name (default: auto-generated with timestamp)

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if log_to_file and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Generate log filename if not provided
    if log_to_file and log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"query_expansion_{timestamp}.log"

    log_path = os.path.join(log_dir, log_file) if log_to_file else None

    # Create formatter
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_formatter = logging.Formatter("%(levelname)s - %(name)s - %(message)s")

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any existing handlers
    root_logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation
    if log_to_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)

        logging.info(f"Logging to file: {log_path}")

    # Suppress overly verbose loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("googleapiclient").setLevel(logging.WARNING)
    logging.getLogger("google_auth_httplib2").setLevel(logging.WARNING)

    logging.info("Logging configuration complete")
    return root_logger


def get_logger(name):
    """
    Get a logger with the specified name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
