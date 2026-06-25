"""
Logging Configuration
Structured logging for Assessment Rubric Agent
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['service'] = 'assessment-rubric-agent'
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name


def setup_logging(log_level: str = "INFO", log_dir: str = "logs", use_json: bool = True):
    """
    Setup logging configuration.
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files
        use_json: Whether to use JSON formatting
    """
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    if use_json:
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (JSON format)
    file_handler = logging.FileHandler(log_path / "rubric_agent.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(CustomJsonFormatter())
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.FileHandler(log_path / "rubric_agent_errors.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(CustomJsonFormatter())
    root_logger.addHandler(error_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    return root_logger


# Default setup
setup_logging()
