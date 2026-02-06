# omnipy/core/logger.py
import logging
import sys
from typing import Optional

# Global flag to avoid duplicate handlers
_LOGGER_CONFIGURED = False

def setup_logger(
    name: str = "omnipy",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    use_console: bool = True
) -> logging.Logger:
    """
    Create and configure a reusable logger for omnipy modules.
    
    Args:
        name: Logger name (use __name__ in modules)
        level: Logging level (DEBUG, INFO, WARNING, etc.)
        log_file: Optional file path to write logs
        use_console: Whether to output logs to stdout/stderr
    
    Returns:
        Configured logger instance
    """
    global _LOGGER_CONFIGURED
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times in same process
    if logger.handlers and _LOGGER_CONFIGURED:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler (stdout for INFO+, stderr for WARNING+)
    if use_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        # Send WARNING+ to stderr
        console_handler.addFilter(lambda record: record.levelno < logging.WARNING)
        logger.addHandler(console_handler)

        error_handler = logging.StreamHandler(sys.stderr)
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.WARNING)
        logger.addHandler(error_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    logger.propagate = False  # Prevent duplicate logs in parent loggers
    _LOGGER_CONFIGURED = True
    return logger