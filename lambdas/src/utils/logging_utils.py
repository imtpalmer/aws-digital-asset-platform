import os
import logging

def configure_logging():
    """
    Configures the logger's logging level based on the LOGGING_LEVEL environment variable.
    Defaults to INFO if the environment variable is not set or is invalid.
    
    Returns:
        logging.Logger: The configured logger instance.
    """
    # Create or get a logger
    logger = logging.getLogger()

    # Logging level mapping
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    # Set the logging level using the environment variable or default to INFO
    log_level = os.getenv('LOGGING_LEVEL', 'INFO').upper()
    logger.setLevel(log_levels.get(log_level, logging.INFO))

    # Optional: Add handler to log to the console
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)

    return logger