"""
Logging utilities
Centralized logging configuration
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import colorlog


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> None:
    """
    Setup logging configuration
    
    Args:
        level: Logging level
        log_file: Optional log file path
        format_string: Custom format string
    """
    if format_string is None:
        format_string = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Console handler with colors
    console_handler = colorlog.StreamHandler(sys.stdout)
    console_handler.setFormatter(colorlog.ColoredFormatter(
        format_string,
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    
    handlers = [console_handler]
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True
    )


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get logger instance
    
    Args:
        name: Logger name (usually __name__)
        level: Optional logging level override
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if level is not None:
        logger.setLevel(level)
    return logger

